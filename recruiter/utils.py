import pickle
import openai
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import json
import io
import os
import re
import PyPDF2
from requests import Request
from .models import CandidateRanking
from freddie_ai import settings
from dotenv import load_dotenv
import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow



load_dotenv()

# Load OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Google Sheets API authentication
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
CREDS_PATH = os.path.join(os.getenv("VIRTUAL_ENV"), "recruiter.json")
CREDS = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
client = gspread.authorize(CREDS)

# Google Drive API authentication
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]
DRIVE_CREDS_PATH = os.path.join(os.getenv("VIRTUAL_ENV"), "drive-access.json")
DRIVE_CREDS = Credentials.from_service_account_file(DRIVE_CREDS_PATH, scopes=DRIVE_SCOPES)
drive_service = build("drive", "v3", credentials=DRIVE_CREDS)

# Gmail API authentication
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
GMAIL_CREDS = Credentials.from_service_account_file(DRIVE_CREDS_PATH, scopes=GMAIL_SCOPES)
gmail_service = build("gmail", "v1", credentials=GMAIL_CREDS)


# Google Sheet details
SHEET_ID = "1UeYUNPGCfnMA7lOqHSpaVswsfB2FRFZieBqhk9bBD2U"
SHEET_NAME = "Sheet1"

def fetch_candidates_from_sheets():
    """Fetch all candidates' information from Google Sheets."""
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    data = sheet.get_all_records()

    return [
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

def sanitize_filename(filename):
    """Remove special characters and replace spaces with underscores."""
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)

def download_resume(drive_link, candidate_name):
    """Download a resume PDF from Google Drive and save it."""
    try:
        file_id = drive_link.split("/d/")[1].split("/")[0]  # Extract File ID
        sanitized_name = sanitize_filename(candidate_name)
        file_name = f"{sanitized_name}_resume.pdf"
        relative_path = os.path.join("media", "resumes", file_name)
        file_path = os.path.join(settings.BASE_DIR, relative_path)  # Save as absolute path but return relative

        request = drive_service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        file_content = file.getvalue()
        if not file_content:
            print(f"Error: No data received for {candidate_name}")
            return None  

        with open(file_path, "wb") as f:
            f.write(file_content)

        print(f"Successfully downloaded: {file_path}")
        return file_path  
    except Exception as e:
        print(f"Error downloading {candidate_name}'s resume: {e}")
        return None

def download_all_resumes(candidates):
    """Download all candidates' resumes and return a dictionary with file paths."""
    resume_paths = {}

    for candidate in candidates:
        resume_link = candidate.get("resume_link", "")
        fullname = candidate.get("fullname", "")

        if resume_link:
            file_path = download_resume(resume_link, fullname)
            if file_path:
                resume_paths[fullname] = file_path
            else:
                print(f"Failed to download resume for {fullname}")
        else:
            print(f"No resume link for {fullname}")

    return resume_paths

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF resume."""
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    
    return text.strip()

def rank_candidate(resume_path, candidate):
    """Use OpenAI API to rank a candidate based on resume and screening answers."""
    openai.api_key = os.getenv("OPENAI_API_KEY")
    resume_text = extract_text_from_pdf(resume_path)

    prompt = f"""
    Rate this candidate's fit for a marketing officer role on a scale of 0-100.
    Consider experience, skills, and cultural fit.

    Resume:
    {resume_text}

    Screening Answers:
    - Strengths: {candidate.get("screening_q1", "Not provided")}
    - Weaknesses: {candidate.get("screening_q2", "Not provided")}
    - Availability: {candidate.get("screening_q3", "Not provided")}

    Score (0-100):
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )

        score_text = response.choices[0].message.content.strip()
        score_match = re.search(r'\d+', score_text)
        score = int(score_match.group()) if score_match else 0

        return score

    except Exception as e:
        print(f"Error ranking candidate {candidate['fullname']}: {e}")
        return 0



def process_candidates(candidates):
    """Ranks candidates and saves results to the database."""
    ranked_candidates = []

    for candidate in candidates:
        resume_path = candidate["resume_path"]  # Ensure this exists
        score = rank_candidate(resume_path, candidate)

        # Save to DB
        candidate_entry = CandidateRanking.objects.create(
            fullname=candidate["fullname"],
            email=candidate["email"],
            score=score,
            resume_link=candidate["resume_link"],
            screening_q1=candidate["screening_q1"],
            screening_q2=candidate["screening_q2"],
            screening_q3=candidate["screening_q3"],
        )

        ranked_candidates.append(candidate_entry)

    print("All candidates ranked & saved to database!")
    return ranked_candidates


def authenticate_gmail():
    """Authenticate and return Gmail service."""
    creds = None

    # Load token if it exists
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token_file:
            creds = pickle.load(token_file)

    # If credentials are invalid or missing, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open("token.pkl", "wb") as token_file:
            pickle.dump(creds, token_file)

    return build("gmail", "v1", credentials=creds)


def send_email(service, candidate):
    """Send an email to high-ranking candidates using Gmail API."""
    sender_email = "knonxho@gmail.com"  # Your actual Gmail address
    recipient = candidate["email"]
    subject = "Next Steps in Your Application"
    
    message_body = f"""
    Hi {candidate['fullname']},

    Thanks for applying! Based on our initial screening, we'd like to move forward with your application.

    Regards,  
    Recruitment Team
    """

    message = MIMEText(message_body)
    message["From"] = sender_email  # Add sender email
    message["To"] = recipient
    message["Subject"] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        print(f"Email sent to {candidate['fullname']} ({recipient})")
    except Exception as e:
        print(f"Error sending email to {candidate['fullname']}: {e}")
