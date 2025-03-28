import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import json
import io
import os

from freddie_ai import settings

# from ai_recruiter.freddie_ai import settings

# Google Sheets API authentication
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
CREDS_PATH = os.path.join(os.getenv("VIRTUAL_ENV"), "recruiter.json")
CREDS = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
client = gspread.authorize(CREDS)

# Google Sheet details
SHEET_ID = "1TPntAcoFPZVCFp-4kYgnqcaWGn5BGeuadU0okc6yWvs"
SHEET_NAME = "Sheet1"

def fetch_candidates_from_sheets():
    """Fetch all candidates' information from Google Sheets, display in console, and return as JSON."""
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    data = sheet.get_all_records()

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

    return candidates

# Google Drive API authentication
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]
DRIVE_CREDS_PATH = os.path.join(os.getenv("VIRTUAL_ENV"), "drive-access.json")
DRIVE_CREDS = Credentials.from_service_account_file(DRIVE_CREDS_PATH, scopes=DRIVE_SCOPES)
drive_service = build("drive", "v3", credentials=DRIVE_CREDS)

import re
import os

def sanitize_filename(filename):
    """Remove special characters and replace spaces with underscores."""
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)

def download_resume(drive_link, candidate_name):
    """Download a resume PDF from Google Drive and save it with the candidate's name."""
    file_id = drive_link.split("/d/")[1].split("/")[0]  # Extract File ID

    # Generate a sanitized file name using candidate name
    sanitized_name = sanitize_filename(candidate_name)
    file_name = f"{sanitized_name}_resume.pdf"
    file_path = os.path.join(settings.MEDIA_ROOT, "resumes", file_name)

    # Download from Google Drive
    request = drive_service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    file_content = file.getvalue()
    if not file_content:
        print("Error: No data received from Google Drive.")
        return None  # Handle failure

    # Save the file in binary mode
    with open(file_path, "wb") as f:
        f.write(file_content)

    print(f"Successfully downloaded: {file_path}")
    return file_path  # Return the saved file path
