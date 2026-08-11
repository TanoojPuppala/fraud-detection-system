# Cloud Deployment Guide — Fraud Detection & Risk Analysis System

This guide explains how to deploy the **Fraud Detection System** to free-tier cloud platforms (**Render**, **Vercel**, and **Neon PostgreSQL**).

---

## Architecture Options

### Option A: Unified Single-Server Web App (Recommended — Easiest & Cleanest)
Deploy both FastAPI Backend and React Dashboard as a **single web service** on **Render**.
- **URL**: `https://fraud-detection-system.onrender.com`
- **Cost**: 100% Free (Render Free Web Service Tier)
- **Features**: Single URL hosts both the React UI dashboard (`/`) and API endpoints (`/api/v1` & `/docs`).

---

### Option B: Decoupled Multi-Cloud Stack (Vercel + Render + Neon)
1. **Frontend**: Host on **Vercel** (Free Edge Network)
2. **Backend**: Host on **Render** (Free FastAPI Web Service)
3. **Database**: Host on **Neon** (Free Serverless PostgreSQL)

---

## Option A Deployment Instructions (Render Unified Web App)

### Step 1: Push Code to GitHub
Ensure all latest code is committed and pushed to your GitHub repository:
```bash
git add .
git commit -m "feat: prepare unified cloud deployment"
git push origin main
```

### Step 2: Deploy on Render
1. Go to [Render Dashboard](https://dashboard.render.com/) and log in with GitHub.
2. Click **New +** -> Select **Web Service**.
3. Connect your GitHub repository: `TanoojPuppala/fraud-detection-system`.
4. Configure the Web Service settings:
   - **Name**: `fraud-detection-system`
   - **Environment**: `Python 3`
   - **Region**: `Oregon (US West)`
   - **Branch**: `main`
   - **Build Command**:
     ```bash
     pip install -r backend/requirements.txt && cd frontend && npm install && npm run build
     ```
   - **Start Command**:
     ```bash
     uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
     ```
5. Click **Create Web Service**.

*Render will automatically build the React assets, initialize the FastAPI backend, and launch the single unified application!*

---

## Option B Database Setup (Neon PostgreSQL)

1. Sign up for a free account at [Neon.tech](https://neon.tech/).
2. Create a new PostgreSQL database project named `fraud_detection`.
3. Copy your connection string from the Neon dashboard (e.g., `postgresql://user:pass@ep-cool-db.neon.tech/fraud_detection?sslmode=require`).
4. On Render, navigate to **Environment** -> **Environment Variables** -> Add:
   - `DATABASE_URL`: paste your Neon PostgreSQL string.

---

## Local Verification Command

Run the unified full-stack web application locally on port 8000:
```bash
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --port 8000
```
Open `http://localhost:8000/` in your browser to view the clean React UI served directly by FastAPI!
