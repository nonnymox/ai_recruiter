import json
import os
from django.http import JsonResponse
from django.views import View
from django.utils.timezone import now  # Ensure this import is present
from .models import CandidateRanking
from .utils import fetch_candidates_from_sheets, download_resume, rank_candidate, send_email,  authenticate_gmail

class DownloadAllResumesView(View):
    """View to download all resumes and return file paths."""

    def get(self, request):
        candidates = fetch_candidates_from_sheets()
        resume_paths = {}

        for candidate in candidates:
            resume_link = candidate.get("resume_link", "")
            if resume_link:
                file_path = download_resume(resume_link, candidate["fullname"])
                
                # Convert to relative path for better API response
                relative_path = file_path.replace(os.getcwd() + os.sep, "") if file_path else "Failed"
                
                resume_paths[candidate["fullname"]] = relative_path

        return JsonResponse({"resumes": resume_paths})


class RankCandidatesView(View):
    """View to rank candidates based on their resumes and store results."""

    def get(self, request):
        candidates = fetch_candidates_from_sheets()
        rankings = []
        gmail_service = authenticate_gmail()

        for candidate in candidates:
            resume_link = candidate.get("resume_link", "")
            if resume_link:
                resume_path = download_resume(resume_link, candidate["fullname"])
                if resume_path and os.path.exists(resume_path):
                    score = rank_candidate(resume_path, candidate)
                    candidate["score"] = score
                    rankings.append(candidate)

                    # Save ranking in the database
                    CandidateRanking.objects.update_or_create(
                        email=candidate["email"],
                        defaults={
                            "fullname": candidate["fullname"],
                            "score": score,
                            "resume_link": resume_link,
                            "screening_q1": candidate.get("screening_q1", ""),
                            "screening_q2": candidate.get("screening_q2", ""),
                            "screening_q3": candidate.get("screening_q3", ""),
                            "created_at": now(),
                        },
                    )

                    # Send email if candidate ranks >= 70
                    if score >= 70:
                        send_email(gmail_service,candidate)

        # Sort candidates by score (highest first)
        rankings.sort(key=lambda x: x["score"], reverse=True)

        return JsonResponse({"rankings": rankings})

class CandidateRankingListView(View):
    """View to return stored candidate rankings as JSON."""

    def get(self, request):
        rankings = CandidateRanking.objects.all().order_by("-score")
        data = [
            {
                "fullname": c.fullname,
                "email": c.email,
                "score": c.score,
                "created_at": c.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for c in rankings
        ]
        return JsonResponse({"rankings": data}, safe=False)

def get_candidates(request):
    """Fetch candidates from Google Sheets and attach their resume paths."""
    candidates = fetch_candidates_from_sheets()
    resume_paths = {}  # Ensure this dictionary is initialized

    for candidate in candidates:
        resume_link = candidate.get("resume_link", "")
        if resume_link:
            file_path = download_resume(resume_link, candidate["fullname"])
            
            # Convert to relative path
            relative_path = file_path.replace(os.getcwd() + os.sep, "") if file_path else "Failed"

            resume_paths[candidate["fullname"]] = relative_path
            candidate["saved_resume"] = relative_path  # Use relative path

    return JsonResponse({"candidates": candidates, "resumes": resume_paths})

class HomeView(View):
    """Home view to display all available API endpoints."""

    def get(self, request):
        endpoints = {
            "Get details of all candidates": "/candidates/",
            "Download all resumes": "/download_resumes/",
            "Rank Candidates": "/rank_candidates/",
            "View Rankings from Database": "/rankings",
            "Admin Login View": "/admin"
        }
        return JsonResponse({"available_endpoints": endpoints})
