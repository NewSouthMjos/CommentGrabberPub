# from .models import Result_row
from django.views import View
from django.shortcuts import render, redirect
from .vk_requests import execute_comments_colletion, Result_row
from .forms import MyRequestInputForm
from datetime import datetime, date, timedelta
from .mytextsfunc import correct_vk_link


class Index(View):
    def get(self, request):
        form = MyRequestInputForm(
            initial={
                "posts_count": 1,
                "posts_offset": 0,
                "request_mode": 0,
                "request_end_date": date.today(),
                "request_start_date": date.today() - timedelta(days=1),
                "client_timezone": 0,
            }
        )
        return render(request, "grabber/unputform.html", {"form": form})


class Results(View):
    def get(self, request, *args, **kwargs):
        form = MyRequestInputForm(request.GET)
        if not (form.is_valid()):
            return render(request, "grabber/unputform.html", {"form": form})

        comment_list = execute_comments_colletion(
            form.cleaned_data['request_adress'],
            form.cleaned_data['posts_count'],
            form.cleaned_data['posts_offset'],
            form.cleaned_data['request_mode'],
            form.cleaned_data['client_timezone'],
            str(form.cleaned_data['request_end_date']),
            str(form.cleaned_data['request_start_date']),
        )
        extend_values = {
            "request_adress": correct_vk_link(form.cleaned_data['request_adress']),
            "object_list": comment_list,
            "posts_count": form.cleaned_data['posts_count'],
            "comments_count": len(comment_list),
        }
        return render(request, "grabber/results.html", extend_values)
