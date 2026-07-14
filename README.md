# 🚀 ResumeAI – Smart Resume Parser & Portfolio Builder

A production-quality SaaS application that leverages AI to parse resumes, build professional portfolios, and optimize for ATS (Applicant Tracking Systems).

---

## 📋 Project Overview

ResumeAI is a full-stack web application built with **Django REST Framework** (backend) and **React 19** (frontend). The platform will offer:

- **AI-Powered Resume Parsing** – Upload resumes and extract structured data using Gemini AI
- **Portfolio Builder** – Generate beautiful portfolio websites from parsed resume data
- **ATS Optimization** – Score and optimize resumes for Applicant Tracking Systems
- **Dashboard Analytics** – Track resume performance and insights

> **Current Phase:** Phase 1 – Project Foundation (scaffolding, configuration, landing page)

---

## 📁 Folder Structure

```
resume-ai/
│
├── backend/
│   ├── config/                 # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── accounts/           # User authentication & profiles
│   │   ├── resumes/            # Resume CRUD operations
│   │   ├── parser/             # AI resume parsing engine
│   │   ├── portfolio/          # Portfolio generation
│   │   ├── ats/                # ATS scoring & optimization
│   │   └── common/             # Shared utilities & mixins
│   ├── media/                  # User uploaded files
│   ├── static/                 # Static assets
│   ├── requirements.txt
│   ├── .env.example
│   └── manage.py
│
├── frontend/
│   ├── src/
│   │   ├── api/                # Axios instance & API helpers
│   │   ├── assets/             # Images, fonts, static files
│   │   ├── components/         # Reusable UI components
│   │   ├── contexts/           # React Context providers
│   │   ├── hooks/              # Custom React hooks
│   │   ├── layouts/            # Page layout wrappers
│   │   ├── pages/              # Route-level page components
│   │   ├── routes/             # React Router configuration
│   │   ├── services/           # Business logic & API services
│   │   ├── styles/             # CSS stylesheets
│   │   ├── utils/              # Helper functions
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

---

## 🛠️ Installation

### Prerequisites

- Python 3.13+
- Node.js 18+
- PostgreSQL 15+
- Git

---

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Resume_GP
```

### 2. Backend Setup

```bash
# Create and activate virtual environment
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your database credentials and secret key
```

### 3. Database Setup

```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE resumeai_db;
\q

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 4. Frontend Setup

```bash
cd frontend
npm install
```

---

## 🔐 Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Django secret key | `django-insecure-xxx` |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hostnames | `localhost,127.0.0.1` |
| `DB_NAME` | PostgreSQL database name | `resumeai_db` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `your_password` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |

---

## 🚀 Run Commands

### Backend (Django)

```bash
cd backend
python manage.py runserver
```

Backend runs at: `http://localhost:8000`

### Frontend (React + Vite)

```bash
cd frontend
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## 🗺️ Future Roadmap

| Phase | Feature | Status |
|---|---|---|
| Phase 1 | Project Foundation | ✅ Complete |
| Phase 2 | Authentication (JWT) | ✅ Complete |
| ... | ... | ... |
| Phase 16 | Admin Intelligence Dashboard | ✅ Complete |
| Phase 17 | Notification Platform | ✅ Complete |

---

## 📄 License

This project is proprietary. All rights reserved.

---

## 👨‍💻 Author

Built with ❤️ using Django, React, and AI.
