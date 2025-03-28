from django.http import JsonResponse
import gspread
from google.oauth2.service_account import Credentials
import json
import os

# Google Sheets API authentication
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


CREDS_PATH = os.path.join(os.getenv("VIRTUAL_ENV"), "recruiter.json")


CREDS = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
client = gspread.authorize(CREDS)

# Google Sheet details
SHEET_ID = "1TPntAcoFPZVCFp-4kYgnqcaWGn5BGeuadU0okc6yWvs"
SHEET_NAME = "Sheet1"

def fetch_candidates(request):
    """Fetch all candidates' information from Google Sheets, display in console, and return as JSON."""
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    data = sheet.get_all_records()

    # Map the data fields correctly
    candidates = [
        {
            "fullname": row.get("Full Name", ""),  
            "email": row.get("Email", ""),  
            "resume_link": row.get("Resume Link", ""),  
            "screening_q1": row.get("Screening Q1 (What are your key strengths?)", ""),  
            "screening_q2": row.get("Screening Q2 (What is your biggest weakness?)", ""),  
            "screening_q3": row.get("Screening Q3 (Are you available immediately?)", "")  
        }
        for row in data
    ]

    # Print candidates data to the console in a readable format
    print("\nFetched Candidates Data:")
    print(json.dumps(candidates, indent=4))

    return JsonResponse({"candidates": candidates}, safe=False)
