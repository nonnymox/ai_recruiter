from django.urls import path
from .views import fetch_candidates

urlpatterns = [
    path("candidates/", fetch_candidates, name="fetch_candidates"),
]
