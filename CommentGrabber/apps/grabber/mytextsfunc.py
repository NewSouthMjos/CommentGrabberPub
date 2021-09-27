def cut_text(long_text, max_words=6, max_chars=30):
    """
    Cut the text for not longer chars than max_chars +3 (adding ...)
    and no longer than max_words.
    Note: if there is first spacechar and then more than max_chars
    symbols: return just " ..."
    """
    long_text = long_text.replace("\n", " ")
    words_list = long_text.split(" ", maxsplit=max_words)
    if len(" ".join(words_list)) < max_chars:
        return " ".join(words_list)
    if len(words_list) > 1:
        while len(" ".join(words_list)) > max_chars:
            words_list = words_list[:-1]
            if len(words_list) == 1:
                return words_list[0][:max_chars] + "..."
    else:
        return words_list[0][:max_chars] + "..."
    return " ".join(words_list) + "..."


def correct_vk_link(user_link):
    if type(user_link) == str:
        user_link = user_link.removeprefix("https://")
        user_link = user_link.removeprefix("http://")
        user_link = user_link.removeprefix("vk.com/")
    return user_link


def main():
    # example = cut_text(input())
    example = cut_text(
        """"Усадьба Орловых-Давыдовых

53°23'34.3"N 49°04'30.8"E

Фото: Алексей Авдейчев"""
    )
    print(f"обрезанный: {example}")

    example2 = correct_vk_link("https://vk.com/welovegames")
    print(f"example2: {example2}")

    assert correct_vk_link("https://vk.com/welovegames") == "welovegames"
    assert correct_vk_link("http://vk.com/welovegames") == "welovegames"
    assert correct_vk_link("vk.com/welovegames") == "welovegames"
    assert correct_vk_link("vk.com/vkcomhttps") == "vkcomhttps"


if __name__ == "__main__":
    main()
