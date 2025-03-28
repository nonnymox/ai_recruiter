from django.urls import path
from .views import get_candidates, DownloadResumeView

urlpatterns = [
    path("candidates/", get_candidates, name="get_candidates"),
    path("download-resume/<str:candidate_name>/", DownloadResumeView.as_view(), name="download_resume"),]