from django.urls import path
from .views import get_candidates, DownloadAllResumesView, RankCandidatesView, HomeView, CandidateRankingListView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("candidates/", get_candidates, name="get_candidates"),
    path("download_resumes/", DownloadAllResumesView.as_view(), name="download_all_resumes"),
    path("rank_candidates/", RankCandidatesView.as_view(), name="rank_candidates"),
    path("rankings/", CandidateRankingListView.as_view(), name="candidate-rankings"),
]
