from django.http import JsonResponse
from django.http import HttpRequest
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
CREDS = Credentials.from_service_account_file("../env/recruiter.json", scopes=SCOPES)
client = gspread.authorize(CREDS)

SHEET_ID = "1TNXMEqEoD2yWTJK4qCIE-VFaQud6CSZ13DSCJckVVX4"
SHEET_NAME = "My Workouts"

def fetch_candidates(request):
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    data = sheet.get_all_records()
    return JsonResponse({"candidates": data})
