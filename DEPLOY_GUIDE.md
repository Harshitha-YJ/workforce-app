# 🚀 Deployment Guide — WorkForce on Render

## What you need
- A free GitHub account → github.com
- A free Render account → render.com (sign up with GitHub)

---

## Step 1 — Push your code to GitHub

### 1a. Create a new GitHub repository
1. Go to github.com → click **"New repository"**
2. Name it: `workforce-app`
3. Keep it **Public**
4. Do NOT tick "Add README" (we already have one)
5. Click **"Create repository"**

### 1b. Push from your computer
Open terminal inside the `employee_mgmt` folder and run:

```bash
git init
git add .
git commit -m "Initial commit — WorkForce Employee Management System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/workforce-app.git
git push -u origin main
```
Replace `YOUR_USERNAME` with your actual GitHub username.

---

## Step 2 — Deploy on Render

### 2a. Connect GitHub to Render
1. Go to **render.com** → Sign in with GitHub
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect a repository"** → select `workforce-app`

### 2b. Configure the service
Fill in these fields:

| Field | Value |
|-------|-------|
| **Name** | workforce-app |
| **Root Directory** | backend |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
| **Plan** | Free |

### 2c. Add environment variables
Click **"Advanced"** → **"Add Environment Variable"**:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | Click "Generate" button |
| `JWT_SECRET_KEY` | Click "Generate" button |

### 2d. Add a PostgreSQL database
1. Click **"New +"** → **"PostgreSQL"**
2. Name: `workforce-db`
3. Plan: **Free**
4. Click **"Create Database"**
5. Copy the **"Internal Database URL"**
6. Go back to your Web Service → Environment Variables
7. Add: `DATABASE_URL` = paste the URL you copied

### 2e. Deploy!
Click **"Create Web Service"** — Render will:
- Install all packages from requirements.txt
- Start gunicorn
- Auto-create all database tables
- Seed the admin user

---

## Step 3 — Get your live URL

After ~3 minutes, Render gives you a URL like:
```
https://workforce-app.onrender.com
```

**That's your live app!** Share it with your college panel.

---

## Default login credentials (production)
| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Employee | Sign up at /signup | your choice |

---

## Troubleshooting

**Build fails?**
- Check the Render logs tab
- Usually a missing package — add it to requirements.txt

**Database error on first run?**
- This is normal — wait 30 seconds and refresh
- Render's free PostgreSQL takes a moment to wake up

**App sleeps after 15 mins (free plan)?**
- Free Render services sleep when not in use
- First request after sleep takes ~30 seconds to wake up
- This is fine for demo/college purposes

---

## 📝 For your college report

Write this in your project documentation:

> "The application is deployed on Render cloud platform using Gunicorn WSGI server with
> PostgreSQL as the production database. The deployment is automated via GitHub integration,
> allowing continuous deployment on every git push."

**Live URL:** https://workforce-app.onrender.com *(update with your actual URL)*
