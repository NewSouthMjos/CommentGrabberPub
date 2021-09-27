from django import forms

# from datetime import datetime
from django.core.exceptions import ValidationError
from .vk_requests import get_group_id


class MyDateInput(forms.DateInput):
    input_type = "date"
    # format=('%YYYY-%m-%d')


class MyRequestInputForm(forms.Form):
    request_adress = forms.CharField(
        label="Ссылка на паблик",
        max_length=300,
        error_messages={"required": "Необходим адрес vk.com"},
    )
    posts_count = forms.IntegerField(
        label="обработать",
        min_value=1,
        max_value=99999,
        error_messages={"min_value": "Неверное число постов обработки в группе"},
    )
    posts_offset = forms.IntegerField(
        label="пропустить первых", min_value=0, max_value=99999
    )
    request_mode = forms.IntegerField(
        label="Режим запроса (спрятать)", min_value=0, max_value=1
    )
    # request_end_date = forms.DateField(label='Дата, с', widget=MyDateInput(), required=False,)
    request_end_date = forms.DateField(
        label="Дата, с",
        widget=MyDateInput(format=("%Y-%m-%d")),
        required=False,
    )
    request_start_date = forms.DateField(
        label="Дата, по",
        widget=MyDateInput(format=("%Y-%m-%d")),
        required=False,
    )
    client_timezone = forms.CharField(max_length=300)
    # mymade_on = forms.DateField(label='Дата')
    # mymade_on = forms.DateField(label='Дата', widget=MyDateInput())

    def clean(self):
        cleaned_data = super().clean()
        request_end_date = cleaned_data.get("request_end_date")
        request_start_date = cleaned_data.get("request_start_date")
        request_adress = cleaned_data.get("request_adress")
        request_mode = cleaned_data.get("request_mode")

        if request_end_date and request_start_date and request_mode == 1:
            if request_end_date < request_start_date:
                msg = "Дата начала сбора постов должна быть раньше или равна конечной дате"
                self.add_error("request_start_date", msg)
                request_start_date = request_end_date
                # raise ValidationError(msg)
        if get_group_id(request_adress) == None:
            msg = "Группа или пользователь по адресу не найдены"
            self.add_error("request_start_date", msg)
