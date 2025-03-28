from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Load credentials
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]
DRIVE_CREDS = Credentials.from_service_account_file("env/drive-access.json", scopes=DRIVE_SCOPES)
drive_service = build("drive", "v3", credentials=DRIVE_CREDS)

def download_resume(drive_link):
    """Download a resume PDF from Google Drive."""
    try:
        file_id = drive_link.split("/d/")[1].split("/")[0]  # Extract File ID
        request = drive_service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        print("✅ Resume downloaded successfully!")
        return file.getvalue()

    except Exception as e:
        print("❌ Error:", e)
        return None

# TEST: Replace with an actual Google Drive resume link
test_drive_link = "https://drive.google.com/file/d/13m2QtAOPTRkBJ6JUzepHZx1CTEef8Y8A/view?usp=sharing"

resume_content = download_resume(test_drive_link)

if resume_content:
    with open("resume.pdf", "wb") as f:
        f.write(resume_content)
    print("✅ File saved as 'resume.pdf'")
else:
    print("❌ Failed to download the resume.")
