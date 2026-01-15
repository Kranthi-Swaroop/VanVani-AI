# VanVani AI: Multilingual Voice Intelligence System

VanVani AI is a zero-internet, voice-based information system designed to bridge the digital and literacy gaps in rural Chhattisgarh, India. This project empowers tribal populations by providing critical information on government schemes, healthcare, and agriculture in their native languages (Gondi, Halbi, Chhattisgarhi, Hindi, and English) through simple phone calls or a web-based interface.

---

## 🚀 Overview: Web Demo vs. Telephony

This repository contains the complete logic for the VanVani AI system. Because telephony services like **Twilio** are paid and require active credit to process phone calls, this project includes a **dedicated Web Interface** to demonstrate the core AI, RAG, and multilingual logic without incurring telephony costs.

- **Telephony Portal**: Handles incoming calls, speech-to-text, and automated voice responses.
- **Web Interface**: A glassy, modern UI that replicates the voice interaction experience directly in the browser.

---

## ✨ Key Features

- 🗣️ **Multilingual Voice Interface**: Supports Gondi, Halbi, Chhattisgarhi, Hindi, and English.
- 🤖 **AI-Powered RAG Engine**: Uses Retrieval-Augmented Generation to answer queries from a specialized knowledge base (PDFs).
- 🎯 **Context-Aware Intent**: Automatically classifies queries into categories like Agriculture, Health, or Schemes for precise filtering.
- 📞 **Zero-Internet Access**: Designed for users with basic feature phones (telephony part).
- 💎 **Premium Web Demo**: High-aesthetic "glassmorphism" web UI with voice visualization and multilingual chat support.

---

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI
- **AI/ML**: Google Gemma (gemma-3-4b-it), Gemini API
- **Vector DB**: ChromaDB
- **Speech**: Sarvam.ai (Indian Languages), Google Cloud STT/TTS
- **Telephony**: Twilio API
- **Database**: SQLAlchemy, SQLite (aiosqlite)
- **Frontend**: Vanilla HTML/CSS/JS with FontAwesome & Google Fonts

---

## ⚙️ Setup & Installation

### 1. Prerequisite Checks
Ensure you have **Python 3.10+** installed.

### 2. Automatic Setup
Run the setup script to create the virtual environment, install dependencies, and initialize folders:
```powershell
.\setup.ps1
```

### 3. Configure Environment
1. Copy `.env.example` to `.env`.
2. Add your **GOOGLE_GEMINI_API_KEY**.
3. (Optional) Add Twilio and Sarvam.ai keys if you wish to use the full telephony system.

### 4. Initialize Knowledge Base
Add your PDF documents to `data/raw_pdfs/` and run:
```powershell
python -m app.database.init_db
```

---

## 🏃 Running the Project

### Start the Server
```powershell
.\run.ps1
```

### Access the Web Demonstration
Open your browser and navigate to:
**[http://localhost:8000/static/index.html](http://localhost:8000/static/index.html)**

---

## 📖 Project Structure

- `app/main.py`: Core FastAPI application and webhooks.
- `app/ai/`: RAG engine and LLM integration logic.
- `app/speech/`: Speech-to-Text and Text-to-Speech modules.
- `app/database/`: Vector storage and historical conversation tracking.
- `app/static/`: Premium web demonstration interface.
- `data/raw_pdfs/`: Source knowledge base for the AI.

---

## ⚖️ License
MIT License.
