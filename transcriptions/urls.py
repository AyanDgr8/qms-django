# transcriptions_project/transcriptions/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('transcriptions/', views.get_transcriptions, name='get_transcriptions'),
    path('search-transcriptions/', views.search_transcriptions, name='search_transcriptions'),
]
