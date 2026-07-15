FROM python:3.11-slim

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set workspace directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm || true

# Copy backend files
COPY . /app/

# Compile static files for production WhiteNoise serving
RUN python manage.py collectstatic --noinput

# Create group and user to run the container as non-root
RUN groupadd -r django && useradd -r -g django django-user
RUN chown -R django-user:django /app

USER django-user

# Port expose
EXPOSE 8000

# Default entrypoint (will be overridden in docker-compose if needed)
CMD ["gunicorn", "--config", "gunicorn.conf.py", "config.wsgi:application"]
