# Production Deployment Guide & Infrastructure Operations

This document outlines the architecture, environment configurations, deployment commands, monitoring details, and verification steps for deploying ResumeAI in production.

---

## 🏗️ Architecture Design

ResumeAI uses a multi-container network topology designed for security and scalability:

```
                  ┌──────────────────────┐
                  │    Internet/User     │
                  └──────────┬───────────┘
                             │ (Port 80/443)
                             ▼
                  ┌──────────────────────┐
                  │    Nginx Ingress     │
                  └────┬────────────┬────┘
        (Static)       │            │ (REST API)
        ┌──────────────┘            └──────────────┐
        ▼                                          ▼
┌──────────────┐                            ┌──────────────┐
│  React App   │                            │  Gunicorn    │
│  (Frontend)  │                            │  (Django)    │
└──────────────┘                            └──────┬───────┘
                                                   │
                            ┌──────────────┬───────┴──────┬──────────────┐
                            ▼              ▼              ▼              ▼
                     ┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
                     │ PostgreSQL   ││ Redis Cache  ││ Celery Worker││ Celery Beat  │
                     │ (Database)   ││ / Broker     ││ (Background) ││ (Scheduler)  │
                     └──────────────┘└──────────────┘└──────────────┘└──────────────┘
```

*   **Nginx Ingress:** Serves static files, user media uploads, acts as SSL termination, and filters traffic with rate-limiting.
*   **Gunicorn Web Server:** Manages multithreaded backend request processes in an isolated network environment.
*   **Redis Cache & Broker:** Serves as high-speed query cache and Celery queue broker.
*   **Celery Worker & Beat:** Asynchronously executes processing tasks (resume analysis, AI generation, weekly emails) in background threads.

---

## 🔐 Environment Configurations

Prepare a production `.env` file in the project root:

```env
# General Settings
SECRET_KEY=generate-a-secure-random-key-for-production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# PostgreSQL Database Keys
DB_NAME=resumeai_db
DB_USER=resume_db_admin
DB_PASSWORD=securepasswordhere
DB_HOST=db
DB_PORT=5432

# Redis Cache URL & Broker Config
REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# File Storage & Log Settings
LOG_FILE_PATH=/app/media/logs/resumeai.log
GEMINI_API_KEY=AIzaSyYourGeminiApiKeyHere
```

---

## 🚀 Execution & Deployment Commands

### 1. Build and Start Services
Compile and start all containers in detached mode:
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

### 2. Apply Migrations & Collect Static Files
Execute database updates and aggregate backend assets inside the container:
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

### 3. Check Active Logs
Check Gunicorn or Nginx activity streams:
```bash
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f nginx
```

---

## 🩺 Monitoring & Diagnostics

Query the diagnostic endpoints to verify service metrics:

*   **Uptime & Ping Check:** `http://localhost/api/health/`
*   **Database Sync Check:** `http://localhost/api/health/db/`
*   **Redis Connection Check:** `http://localhost/api/health/cache/`
*   **Celery Daemon Check:** `http://localhost/api/health/celery/`
*   **Host Resource Check:** `http://localhost/api/health/system/`

---

## 💾 Backup Procedures & Cron Scheduling

The backup shell script `scripts/backup.sh` should be configured to run nightly.

1.  Make the script executable:
    ```bash
    chmod +x scripts/backup.sh
    ```
2.  Add a crontab entry for a 2:00 AM daily run:
    ```bash
    0 2 * * * /bin/bash /path/to/Resume_GP/scripts/backup.sh > /dev/null 2>&1
    ```

---

## 📋 Infrastructure Verification Checklist

- [ ] Verify that all 7 containers return a status of `Up (healthy)`.
- [ ] Confirm `DEBUG` is set to `False` in Django settings.
- [ ] Validate `/api/health/` endpoints all return `200 OK` with `"status": "healthy"`.
- [ ] Upload a mock document and check `celery` container logs to confirm background parsing triggers correctly.
- [ ] Verify Nginx serves backend media uploads under `/media/...` and does not forward static file queries to Python.
