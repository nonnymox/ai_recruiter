import json
import os
from django.http import JsonResponse
from django.views import View
from .utils import fetch_candidates_from_sheets, download_resume, rank_candidate

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
    """View to rank candidates based on their resumes."""

    def get(self, request):
        candidates = fetch_candidates_from_sheets()
        rankings = []

        for candidate in candidates:
            resume_link = candidate.get("resume_link", "")
            if resume_link:
                resume_path = download_resume(resume_link, candidate["fullname"])
                if resume_path and os.path.exists(resume_path):
                    score = rank_candidate(resume_path, candidate)
                    candidate["score"] = score
                    rankings.append(candidate)

        rankings.sort(key=lambda x: x["score"], reverse=True)  # Sort candidates by score

        return JsonResponse({"rankings": rankings})


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
