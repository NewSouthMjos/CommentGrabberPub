from django.test import TestCase, SimpleTestCase
from grabber.mytextsfunc import cut_text, correct_vk_link
from grabber.mytimefunc import get_localtime_posix_intervals
from grabber.forms import MyRequestInputForm
from grabber.vk_requests import get_group_id, get_posts, get_comments, parse_comment

class Tests(TestCase):
    def test_index_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
 
    # def test_results_status_code(self):
    #     response = self.client.get('/results/')
    #     self.assertEqual(response.status_code, 200)


class TextTests(SimpleTestCase):
    def test_cut_text(self):
        self.assertEquals(cut_text(
            """"Усадьба Орловых-Давыдовых

53°23'34.3"N 49°04'30.8"E

Фото: Алексей Авдейчев""") , """"Усадьба Орловых-Давыдовых ...""")


    def test_correct_vk_link_1(self):
        self.assertEqual(correct_vk_link("https://vk.com/welovegames"), "welovegames")
    def test_correct_vk_link_2(self):
        self.assertEqual(correct_vk_link("http://vk.com/welovegames"), "welovegames")
    def test_correct_vk_link_3(self):
        self.assertEqual(correct_vk_link("vk.com/welovegames"), "welovegames")
    def test_correct_vk_link_4(self):
        self.assertEqual(correct_vk_link("vk.com/vkcomhttps"), "vkcomhttps")

class TimeTests(SimpleTestCase):
    def test_get_localtime_posix_intervals_1(self):
        self.assertEqual(
            (1630695599, 1630609200), get_localtime_posix_intervals(
                "2021-09-03", "2021-09-03", "Asia/Yekaterinburg"
            )
        )

    def test_get_localtime_posix_intervals_2(self):
        self.assertEqual(
            (1630699199, 1630612800), get_localtime_posix_intervals(
            "2021-09-03", "2021-09-03", "Europe/Samara"
            )
        )    
    
    def test_get_localtime_posix_intervals_3(self):
        self.assertEqual(
            (1609718399, 1609459200), get_localtime_posix_intervals(
            "2021-01-03", "2021-01-01", "Etc/UTC"
            )
        )
    def test_get_localtime_posix_intervals_4(self):
        self.assertEqual(
            (1514872799, 1514786400), get_localtime_posix_intervals(
            "2018-01-01", "2018-01-01", "Etc/GMT+6"
            )
        )        
    def test_get_localtime_posix_intervals_1(self):
        self.assertEqual(
            (1456757999, 1456671600), get_localtime_posix_intervals(
            "2016-02-29", "2016-02-29", "Asia/Seoul"
            )
        )

class FormTests(SimpleTestCase):
    def test_MyRequestInputForm_1(self):
        form1 = MyRequestInputForm(data={
            'request_adress' : 'durov', 
            'posts_count' : 5, 
            'posts_offset' : 2, 
            'request_mode' : 0, 
            'client_timezone' : 'Europe/Samara', 
            'request_start_date' : '2021-09-06', 
            'request_end_date' : '2021-09-06',
        })
        #print(form1.errors)
        self.assertTrue(form1.is_valid())
    def test_MyRequestInputForm_2(self):
        form2 = MyRequestInputForm(data={
            'request_adress' : 'durov', 
            'posts_count' : 5, 
            'posts_offset' : 2, 
            'request_mode' : 0, 
            'client_timezone' : 'Europe/Samara',
        })
        #print(form2.errors)
        self.assertTrue(form2.is_valid())
    def test_MyRequestInputForm_3(self):
        form3 = MyRequestInputForm(data={
            'request_adress' : 'durov', 
            'posts_count' : 1, 
            'posts_offset' : 0, 
            'request_mode' : 1, 
            'client_timezone' : 'Europe/Samara',
            'request_start_date' : '2021-09-06', 
            'request_end_date' : '2021-09-10',
        })
        #print(form3.errors)
        self.assertTrue(form3.is_valid())
    def test_MyRequestInputForm_4(self):
        form4 = MyRequestInputForm(data={
            'request_adress' : 'durov', 
            'posts_count' : 1, 
            'posts_offset' : 0, 
            'request_mode' : 1, 
            'client_timezone' : 'Europe/Samara',
            'request_start_date' : '2021-09-06', 
            'request_end_date' : '2021-09-01',
        })
        #print(form4.errors)
        self.assertFalse(form4.is_valid())
    def test_MyRequestInputForm_5(self):
        form5 = MyRequestInputForm(data={
            'request_adress' : 'notvalidvklink_3j4t9ijeidfmvigj9854ngjdnfklg', 
            'posts_count' : 1, 
            'posts_offset' : 0, 
            'request_mode' : 0, 
            'client_timezone' : 'Europe/Samara',
        })
        #print(form5.errors)
        self.assertFalse(form5.is_valid())

class VkTests(SimpleTestCase):
    def test_get_group_id_1(self):
        self.assertEqual(get_group_id('durov'), 1, msg='get_group_id durov failed')
    def test_get_group_id_2(self):
        self.assertEqual(get_group_id('notvalidvklink_3j4t9ijeidfmvigj9854ngjdnfklg'), None, msg='not valid link error')

    def test_get_posts_1(self):
        self.assertEqual(get_posts(None), [])