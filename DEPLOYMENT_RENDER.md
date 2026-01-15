# Deployment Guide: VanVani AI on Render

This guide explains how to deploy the VanVani AI project to **Render**.

## 1. Prerequisites
- A **Render** account (free or paid).
- Your project pushed to a **GitHub** or **GitLab** repository.
- A **Google Gemini API Key**.

## 2. Configuration Files

### `render.yaml` (Included)
The project includes a `render.yaml` file (Blueprint). This automates the setup of your web service and environment variables.

### Port Binding
Render automatically provides a `$PORT` environment variable. The start command is configured as:
`uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 3. Deployment Steps

### Method A: Using Blueprints (Fastest)
1. Go to the [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** and select **Blueprint**.
3. Connect your GitHub repository.
4. Render will detect the `render.yaml` file and set up the service.
5. Provide the required environment variables when prompted.

### Method B: Manual Manual Web Service
1. Click **New +** -> **Web Service**.
2. Connect your repository.
3. Set the following:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add **Environment Variables** (see below).

## 4. Required Environment Variables
You must set these in the Render Dashboard (under the **Env Vars** tab):

| Variable | Description |
| :--- | :--- |
| `GOOGLE_GEMINI_API_KEY` | Your Google AI API key (Required) |
| `ENVIRONMENT` | Set to `production` |
| `DATABASE_URL` | Defaults to `sqlite:///./data/vanvani.db` |
| `VECTOR_DB_PATH` | Defaults to `./data/vector_store` |

## 5. Handling Data Persistence (Important)
Render's free tier has an ephemeral file system (files are deleted when the service restarts). To keep your knowledge base and conversation history:

### Option 1: Render Persistent Disk (Paid)
1. In your Render service settings, go to **Disk**.
2. Add a disk (e.g., 1GB) and mount it to `/data`.
3. Update your `.env` or Render environment variables to point `DATABASE_URL` and `VECTOR_DB_PATH` inside the `/data` folder.

### Option 2: Pre-loading Data (Free Tier)
1. Run `python -m app.database.init_db` locally to generate your `vanvani.db` and `vector_store`.
2. Commit these files to your Git repository (remove them from `.gitignore` first).
3. **Warning**: This makes the knowledge base "Read-Only" because any changes made while the app is running on Render will be lost on the next deployment or restart.

## 6. Telephony (Twilio)
If using Twilio, remember to update your Twilio Webhook URL to your new Render URL:
`https://your-app-name.onrender.com/webhook/incoming-call`
