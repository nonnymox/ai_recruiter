from django.urls import path
from .views import fetch_candidates

urlpatterns = [
    path("fetch-candidates/", fetch_candidates, name="fetch_candidates"),
]
