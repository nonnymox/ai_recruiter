# AI Recruiter App

A backend automation system designed to streamline the AI-driven hiring process. It integrates Google Sheets, Google Drive, OpenAI API, and Gmail API to automatically fetch candidate data, evaluate resumes and screening responses, and send interview invitations based on AI-generated scores.

## Features

- AI-based candidate ranking
- Email notifications via Gmail API
- Secure authentication using OAuth credentials
- Ranking shown on Admin panel

---

## Installation

### **1 Clone the Repository**

```bash
git clone https://github.com/nonnymox/ai_recruiter.git
cd ai_recruiter
```

### **2 Create and Activate Virtual Environment**

#### On Windows:

```bash
python -m venv env
env\Scripts\activate
```

#### On macOS/Linux:

```bash
python3 -m venv env
source env/bin/activate
```

### **3 Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4 Set Up Environment Variables**

Copy the `.env.example` file and create a `.env` file in same folder:

Edit `.env` to include only the OpenAI API key:

```ini
OPENAI_API_KEY=your_openai_key
```

### **5 Place OAuth Credentials**

Ensure `credentials.json` is inside the root folder for correct authentication

```
ai_recruiter/credentials.json
```

Also, the **service account file** should be inside `venv/`:

```
venv/service_account.json
```

### **6️ Run Migrations**

```bash
python manage.py migrate
```

### **7️ Start the Development Server**

```bash
python manage.py runserver
```

The app will be available at: **http://127.0.0.1:8000/**

---

## View in admin panel

Create new superuser

```bash
python manage.py createsuperuser
```

---

## Docker (Optional)

If you want to containerize your app:

```dockerfile
FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

---

## API Endpoints
``` bash
Get details of all candidates: "/candidates/"
Download all resumes: "/download_resumes/"
Rank Candidates: "/rank_candidates/"
View Rankings from Database: "/rankings"
Admin Login View: "/admin" ```
