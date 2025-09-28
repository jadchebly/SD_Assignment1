# SD_Assignment1
Grades Tracker App

# Grade & What-If Tracker

Simple app to track course assessments, compute current weighted grade, show remaining weight, and run what-if targets.

## Run backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn backend.app:app --reload

## Run Frontend
cd frontend
python3 -m http.server 5500


Open http://127.0.0.1:5500/index.html