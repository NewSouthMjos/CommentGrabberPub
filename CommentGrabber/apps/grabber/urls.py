from django.urls import path

from .views import Index, Results

urlpatterns = [
    path('results', Results.as_view(), name='results'),
    path('', Index.as_view(), name='index'),  
 ]
