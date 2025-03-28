import json
from django.http import JsonResponse, FileResponse
from django.shortcuts import get_object_or_404
from .utils import fetch_candidates_from_sheets, download_resume  # Import functions
import os
from django.views import View

def get_candidates(request):
    """Django view to fetch candidates from Google Sheets."""
    candidates = fetch_candidates_from_sheets()
    return JsonResponse({"candidates": candidates})

class DownloadResumeView(View):
    def get(self, request, candidate_name):
        """Display a candidate's resume in the browser."""
        candidates = fetch_candidates_from_sheets()

        # Normalize candidate name to match the URL format
        formatted_name = candidate_name.replace("_", " ").lower()

        # Find the candidate with the given name
        candidate = next((c for c in candidates if c["fullname"].lower() == formatted_name), None)
        if not candidate:
            return JsonResponse({"error": "Candidate not found"}, status=404)

        resume_link = candidate.get("resume_link", "")
        if not resume_link:
            return JsonResponse({"error": "Resume link not available"}, status=400)

        # Download the resume
        file_path = download_resume(resume_link, candidate["fullname"])
        if not file_path or not os.path.exists(file_path):
            return JsonResponse({"error": "Failed to download resume"}, status=500)

        # ✅ Display PDF in browser instead of downloading
        response = FileResponse(open(file_path, "rb"), content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{os.path.basename(file_path)}"'  # Use 'inline' instead of 'attachment'
        return response