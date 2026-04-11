# Alzheimer Disease Detection System

## Overview

This repository contains a full-stack Alzheimer’s disease detection application with:
- a Django REST API backend for user authentication, diagnosis prediction, and report management
- a React + Vite frontend for admin, doctor, and patient dashboards
- an MRI scan analysis model with explainability support
- JWT authentication and role-based access control

## Architecture

- Backend: `ADD-Backend`
  - Django 6
  - Django REST Framework
  - PostgreSQL (Supabase configuration supported)
  - JWT authentication via `djangorestframework_simplejwt`
  - CORS enabled for frontend access
  - Custom user model in `accounts`
  - Diagnosis workflow in `diagnosis`
  - ML model and explainers in `diagnosis/ml_model`

- Frontend: `ADD-Frontend`
  - React 18
  - Vite
  - Tailwind CSS
  - React Router DOM
  - Role-based dashboard layouts and pages for:
    - admin
    - doctor
    - patient

## Features

### Admin
- View dashboard stats
- Approve or reject doctor registrations
- Manage users and roles

### Doctor
- Upload MRI scans
- Create diagnosis requests
- Access patient list and scan history
- View detailed prediction results
- Download PDF reports

### Patient
- View own report history
- Access latest scan results
- See doctor-provided diagnostic summaries

### Diagnosis & ML
- Image-based disease prediction
- Explainability using LIME, SHAP, and Grad-CAM
- Store results as `DiagnosisResult` records
- Serve scan details and report metadata via API

## Project Structure

```text
ADD-Backend/
  accounts/
  diagnosis/
  core/
  media/
  requirements.txt

ADD-Frontend/
  public/
  src/
  package.json
```

## Backend Setup

1. Open a terminal and go to the backend folder:
   ```bash
   cd "d:\AI PROJECT\ADD-Backend"
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the backend server:
   ```bash
   python manage.py runserver
   ```

6. Default backend URL:
   - `http://127.0.0.1:8000/`

## Frontend Setup

1. Open a terminal and go to the frontend folder:
   ```bash
   cd "d:\AI PROJECT\ADD-Frontend"
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Default frontend URL:
   - typically `http://127.0.0.1:5173/`

## API Endpoints

### Accounts
- `POST /api/accounts/register/`
- `POST /api/accounts/login/`
- `GET /api/accounts/me/`
- `POST /api/accounts/token/refresh/`
- `GET /api/accounts/pending-doctors/`
- `POST /api/accounts/approve/<user_id>/`
- `POST /api/accounts/reject/<user_id>/`
- `GET /api/accounts/users/`

### Diagnosis
- `POST /api/diagnoses/predict/`
- `GET /api/diagnoses/health/`
- `GET /api/diagnoses/doctor/reports/`
- `GET /api/diagnoses/patients/`
- `GET /api/diagnoses/patient/reports/`
- `GET /api/diagnoses/scans/<scan_id>/`


