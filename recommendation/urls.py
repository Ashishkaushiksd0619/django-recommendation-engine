# recommendation/urls.py

from django.urls import path
from .views import contextual_view

urlpatterns = [
    path('contextual/', contextual_view),
]
