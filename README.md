# Integrated Bioinformatics & AI Drug Discovery Workflow

A Flask-based web platform for bioinformatics and drug discovery analysis. Users can submit requests for GEO dataset prioritization, transcriptomics, functional enrichment, target identification, and AI-driven drug discovery. The system supports user registration, email verification, and admin dashboard.

## Features

- User registration with email verification
- Secure login/logout
- Five analysis modules:
  - GEO Dataset Prioritization
  - Transcriptomics Analysis
  - Functional Enrichment
  - Target Identification
  - Drug Discovery
- Request tracking and status updates
- Admin dashboard to manage all requests
- Email notifications to users and admin

## Technologies

- Flask (Python)
- SQLite (or PostgreSQL on Render)
- Flask-Login, Flask-Mail, Flask-SQLAlchemy
- Bootstrap for frontend

## Live Demo

_Add your Render URL once deployed._

## Installation (Local)

1. Clone the repository
2. Create a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Set environment variables (see `.env.example`)
5. Run: `python app.py`

## Deployment

The app is configured for deployment on **Render**. Set the following environment variables in Render:

- `SECRET_KEY`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_DEFAULT_SENDER`
- `ADMIN_EMAIL`
- `DATABASE_URL` (Render provides PostgreSQL)

## Project Structure
