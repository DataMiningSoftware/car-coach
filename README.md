# car-coach

An AI-assisted companion for car enthusiasts (and people who aren't car experts),
focused on the **Malaysian** market. Ask about a car's specs, history, and owner
experiences, get modification advice with JPJ legality reminders, upload vehicle
documents for extraction, and (planned) visualize mods and find the right workshop.

> MVP scope. Image visualization and workshop search are stubs in this build.

## Features

| Feature | Module | Status |
|---|---|---|
| Specs / history / owner remarks Q&A (RAG) | `backend/knowledge.py` | working |
| Modification advisor (gains + cost + JPJ legality) | `backend/mods.py` | working |
| Document upload → OCR → extraction (PII-masked) | `backend/docs.py` | working |
| AI image visualization of mods | `backend/visualize.py` | stub |
| Workshop finder by specialty | `backend/workshops.py` | stub |

## How it works

```
React frontend
      │
FastAPI backend ── Groq (LLM) ── BM25 retrieval over curated car knowledge base
      │                              └─ data/seed/cars.json (specs, remarks, history)
      ├── docs.py  (OCR + PII masking)
      ├── visualize.py (hosted img2img, stub)
      └── workshops.py (Google Places, stub)
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env   # add GROQ_API_KEY
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

## Run the API

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --port 8000
```

## Honest limitations (Malaysia)

- There is **no free public JPJ/chassis/VIN lookup** in Malaysia — cars are
  identified by make/model/year, and previous-owner history is only available via
  documents you upload (JPJ grant, insurance, Puspakom report).
- Modification legality is **advisory** and varies; always verify with JPJ.
- Owner remarks ship as curated seed data and grow via user contributions.

## Privacy

Uploaded registration documents contain personal data (NRIC, phone, email). The
`docs.py` module redacts obvious PII before anything is sent to the LLM. For
stronger coverage, pair with [`pii-guard`](../pii-guard).
