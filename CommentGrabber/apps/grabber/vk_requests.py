import requests

# from mytextsfunc import cut_text
from django.conf import settings
from .mytextsfunc import cut_text, correct_vk_link
from datetime import datetime
from django.db import connection


# from mytimefunc import get_localtime_posix_intervals
from .mytimefunc import get_localtime_posix_intervals

# from time import sleep

import pytz

API_KEY = settings.API_KEY

class WallPost:
    def __init__(self, id, text, comments_count, date: int = None):
        self.id = id
        self.text = text
        self.comments_count = comments_count
        self.date = date


class Result_row:
    def __init__(
        self,
        pk,
        date=0,
        author_name="",
        author_id=0,
        author_link="",
        author_avatar="",
        comment_text="",
        comment_id=0,
        comment_link="",
        parentpost_text="",
        parentpost_link="",
        likescount=0,
    ):
        self.pk = pk
        self.date = date
        self.author_name = author_name
        self.author_id = author_id
        self.author_link = author_link
        self.author_avatar = author_avatar
        self.comment_text = comment_text
        self.comment_id = comment_id
        self.comment_link = comment_link
        self.parentpost_text = parentpost_text
        self.parentpost_link = parentpost_link
        self.likescount = likescount


# sleeptime = 0.05


def execute_comments_colletion(
    request_adress: str,
    posts_count=3,
    posts_offset=0,
    request_mode=0,
    client_timezone=None,
    request_end_date=None,
    request_start_date=None,
):
    """
    Помещает комментарии из группы с адресом request_adress в БД,
    а именно в строки Result_row. Кол-во постов для считывания
    комменатриев posts_count, смещение от самого нового поста
    в группе posts_offset.
    request_mode=0 - по количеству запросов,
    request_mode=1 - по датам
    """
    group_id = get_group_id(request_adress)

    if request_mode == 0:
        posts_list = []
        cur_offset = posts_offset
        flag_end_post_collect: bool = False
        while not (flag_end_post_collect):
            previous_len = len(posts_list)
            suppose_posts_list = get_posts(group_id, count=100, offset=cur_offset)
            for cur_post in suppose_posts_list:
                if len(posts_list) < posts_count:
                    posts_list += [cur_post]
            if len(posts_list) >= posts_count or len(posts_list) == previous_len:
                flag_end_post_collect = True
            cur_offset += 100

    if request_mode == 1:
        end_posix_interval, start_posix_interval = get_localtime_posix_intervals(
            request_end_date, request_start_date, client_timezone
        )
        posts_list = []
        cur_offset = 0
        flag_end_post_collect: bool = False
        while not (flag_end_post_collect):
            suppose_posts_list = get_posts(group_id, count=100, offset=cur_offset)
            if len(suppose_posts_list) > 0:
                can_be_attached_post = suppose_posts_list[0]
                if len(suppose_posts_list) > 1 and cur_offset == 0:
                    suppose_posts_list = suppose_posts_list[1:]
                for cur_post in suppose_posts_list:
                    if start_posix_interval <= cur_post.date <= end_posix_interval:
                        posts_list += [cur_post]
                    if start_posix_interval > cur_post.date:
                        flag_end_post_collect = True
            else:
                flag_end_post_collect = True
            cur_offset += 100
        if start_posix_interval <= can_be_attached_post.date <= end_posix_interval:
            posts_list = [can_be_attached_post] + posts_list
    print(f"Получено постов: {len(posts_list)}")

    comment_list = []
    for iteration, cur_post in enumerate(posts_list):
        print(f"Start collecting comments for post {iteration}...")
        comments_offset = 0
        all_comments_len_for_now = len(comment_list)
        while len(comment_list) < cur_post.comments_count + all_comments_len_for_now:
            previous_len = len(comment_list)
            comment_list += get_comments(
                group_id,
                cur_post,
                count=100,
                offset=comments_offset,
                client_timezone=client_timezone,
            )
            comments_offset += 100

            # если после нового запроса мы не получили новых комментариев - заканчиваем пытаться
            if len(comment_list) == previous_len:
                print(
                    "Breaking the while cycle because there no comments i can get more.."
                )
                break
        print(f"Done collecting comments for post {iteration}!")
    return comment_list


def get_group_id(group_address: str):
    """
    Возвращает id группы по её адресу. Минус в начале - если группа,
    без минуса - пользователь
    """
    url = "https://api.vk.com/method/utils.resolveScreenName"
    params = {
        "access_token": API_KEY,
        "screen_name": correct_vk_link(group_address),
        "v": 5.131,
    }
    res = requests.get(url, params=params)
    res_json = res.json()
    try:
        if res_json["response"]["type"] == "group":
            return -1 * res_json["response"]["object_id"]
        elif res_json["response"]["type"] == "user":
            return res_json["response"]["object_id"]
        else:
            return None
    except TypeError:
        return None


def get_posts(group_id, count=1, offset=0, filter="owner"):
    """
    Возвращает count номеров постов со смещением offset от
    самого нового поста в группе с group_id. max count=100 , ограничение api вконтакте
    """
    if group_id == None:
        return []
    
    url = "https://api.vk.com/method/wall.get"
    params = {
        "access_token": API_KEY,
        "owner_id": group_id,
        "offset": offset,
        "count": count,
        "filter": filter,
        "extended": 0,
        "v": 5.131,
    }
    res = requests.get(url, params=params)
    res_json = res.json()
    posts_list = []
    try:
        for item in res_json["response"]["items"]:
            posts_list += [
                WallPost(
                    item["id"], item["text"], item["comments"]["count"], item["date"]
                )
            ]
        return posts_list
    except TypeError:
        return []


def get_comments(
    group_id, post: WallPost, offset=0, count=100, comment_id=0, client_timezone=None
):
    """
    Возвращает максимально 100 комментариев класса ResultRow с
    группы owner_id с поста post_id. Максимальное число ответов на
    комментарий: 10 (ограничение api вконтакте).
    Так же может возвратить комментарии к комментарию с comment_id.
    """
    url = "https://api.vk.com/method/wall.getComments"
    params = {
        "access_token": API_KEY,
        "owner_id": group_id,
        "post_id": post.id,
        "need_likes": 1,
        "offset": offset,
        "count": count,
        "extended": 1,
        "comment_id": comment_id,
        "thread_items_count": 10,
        "v": 5.131,
    }
    res = requests.get(url, params=params)
    # sleep(sleeptime) #Чтобы не превысить количество запросов в секунду (API VK ограничение)
    res_json = res.json()
    all_comments_list = []

    # заполняем информацию из api-ответа items:
    for comment_json in res_json["response"]["items"]:
        all_comments_list += [
            parse_comment(comment_json, group_id, post, client_timezone)
        ]

        # Обработка ответов к комментарию.
        # Если вы в родительском комментарии, то присутстует thread поле:
        if "thread" in comment_json:
            # Если ВСЕ ответы на комментарий уже получены или их нет:
            if 0 < comment_json["thread"]["count"] <= 10:
                # снова парсим комментарии
                for thread_comment_json in comment_json["thread"]["items"]:
                    all_comments_list += [
                        parse_comment(
                            thread_comment_json, group_id, post, client_timezone
                        )
                    ]

            # Если ответов на комментарий Больше, чем 10: нужен отдельный запрос:
            if comment_json["thread"]["count"] > 10:
                all_comments_list += get_comments(
                    group_id,
                    post,
                    comment_id=comment_json["id"],
                    client_timezone=client_timezone,
                )

    # заполняем информацию из api-ответа profiles и groups, нумеруем комментарии:
    current_comment_number = 1
    for cur_comment in all_comments_list:
        # для пользователей, id у которых положительный:
        if cur_comment.author_id > 0:
            for profile_json in res_json["response"]["profiles"]:
                if profile_json["id"] == cur_comment.author_id:
                    cur_comment.author_name = (
                        profile_json["first_name"] + " " + profile_json["last_name"]
                    )
                    cur_comment.author_avatar = profile_json["photo_50"]
                    break

        # для групп, id у которых отрицательный:
        else:
            for profile_json in res_json["response"]["groups"]:
                if profile_json["id"] == -cur_comment.author_id:
                    cur_comment.author_name = profile_json["name"]
                    cur_comment.author_avatar = profile_json["photo_50"]
                    break
        cur_comment.pk = current_comment_number
        current_comment_number += 1

    for profile_json in res_json["response"]["profiles"]:
        profile_json["first_name"]
        profile_json["last_name"]

    return all_comments_list


def parse_comment(comment_json, group_id, post, client_timezone):
    """
    Принимает комментарий в формате json, обрабатывает,
    расскладывает по полям, и отдаёт объект класса Result_row
    """

    result = Result_row(
        pk=0,
        date=datetime.fromtimestamp(
            comment_json["date"], tz=pytz.timezone(client_timezone)
        ),
        parentpost_text=cut_text(post.text) if post.text else "Запись...",
        parentpost_link="http://vk.com/wall"
        + str(group_id)
        + "_"
        + str(post.id),  # ссылка на родительский пост)
    )
    if "deleted" in comment_json:
        result.comment_text = (
            "Комментарий удалён пользователем или руководителем страницы"
        )
    else:
        # для пользователей, id у которых положительный:
        if comment_json["from_id"] > 0:
            author_link = "http://vk.com/id" + str(comment_json["from_id"])

        # для групп, id у которых отрицательный:
        else:
            author_link = "http://vk.com/public" + str(-1 * comment_json["from_id"])

        result.author_id = comment_json["from_id"]
        result.author_link = author_link
        result.comment_text = comment_json["text"]
        result.comment_id = comment_json["id"]
        result.comment_link = (
            "http://vk.com/wall"
            + str(group_id)
            + "_"
            + str(post.id)
            + "?w=wall"
            + str(group_id)
            + "_"
            + str(post.id)
            + "_r"
            + str(comment_json["id"])
        )  # ссылка на комментарий
        result.likescount = comment_json["likes"]["count"]
    return result


def main():
    group_adr = input("Введите адрес группы: ")
    comment_list = execute_comments_colletion(
        request_adress=group_adr,
        request_mode=1,
        client_timezone="Europe/Lisbon",
        request_end_date="2021-09-06",
        request_start_date="2021-09-06",
    )

    # group_id = get_group_id(group_adr)
    # print(f'Адрес: {group_adr}; id: {group_id}')

    # posts_list = get_posts(group_id, count = 2)
    # print('посты в группе:')
    # for cur_post in posts_list:
    #     print(f'id поста: {cur_post.id}, текст: {cur_post.text}, дата: {cur_post.date}')

    # print('Комментарии первых двух постов:')
    # comment_list = []
    # for cur_post in posts_list:
    #     comment_list += get_comments(group_id, cur_post, count=5, offset=1, client_timezone="Etc/GMT+3")

    print(f"всего собрано комментариев: {len(comment_list)}")
    for cur_comment in comment_list:
        print(
            f"unix-дата: {cur_comment.date} id автора коммента: {cur_comment.author_id}, имя автора ком: {cur_comment.author_name}, аватар автора ком: {cur_comment.author_avatar}, id коммента: {cur_comment.comment_id}, лайков: {cur_comment.likescount}, текст: {cur_comment.comment_text}, к посту: {cur_comment.parentpost_text}, ссылка на пост: {cur_comment.parentpost_link}"
        )
    print(comment_list[0].comment_link)


if __name__ == "__main__":
    main()
