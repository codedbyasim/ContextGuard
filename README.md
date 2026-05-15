# ContextGuard

**Third-Party AI Tool Risk Monitor & Enterprise Security Platform**

Hackathon: Transforming Enterprise Through AI — lablab.ai  
Track: Track 1 — Agent Security & AI Governance  
Deadline: May 19, 2026 — 5:00 AM PKT

---

## Team

| Name   | Role                | Responsibility                      |
| ------ | ------------------- | ----------------------------------- |
| Asim   | AI/ML Integration   | Gemini Risk Engine (gemini.py)      |
| Maira  | Development         | Backend API + Frontend Dashboard    |
| Tayyab | DevOps / Deployment | Lobster Trap + Deploy + Demo Script |

---

## Quick Start

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt

cd ../frontend
npm install
```

### 2. Add your API key

```bash
cp backend/.env.example backend/.env
# Edit backend/.env and add your GEMINI_API_KEY
```

### 3. Start Lobster Trap proxy

```bash
cd lobster
./lobstertrap serve --config policy.yaml
```

### 4. Start backend

```bash
cd backend
uvicorn main:app --reload --port 3000
```

### 5. Start frontend

```bash
cd frontend
npm run dev
```

### 6. Open dashboard

http://localhost:5173

---

## Project Structure

```
contextguard/
├── backend/         ← FastAPI server (Python)
├── frontend/        ← React dashboard
├── lobster/         ← Veea Lobster Trap config
├── demo/            ← Demo data + scripts
└── docs/            ← SRS, Proposal documents
```
