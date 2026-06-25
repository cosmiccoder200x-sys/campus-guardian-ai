# 🛡️ Campus Guardian AI

> Smart Academic Assistant for TKM College of Engineering, Kollam — KTU 2024 Scheme (ECE/EEE)

## Features
- **Attendance Guardian** — Track classes, get risk alerts (Green/Yellow/Red), safe-to-miss calculator
- **Grade Predictor AI** — Enter CIA marks, see predicted SGPA and marks needed for S/A+/A
- **Smart Bunk Planner** — Timetable-based daily/weekly skip recommendations
- **AI Assistant** — Chat interface for academic queries
- **Pre-loaded Subjects** — All S3–S8 TKM KTU 2024 scheme subjects built in
- **Dark/Light Mode** — Persistent theme switching

## Quick Start (Local)

```bash
git clone <repo>
cd campus_guardian
pip install -r requirements.txt
cp .env.example .env
python app.py
```
Open http://localhost:5000

## Deploy to Railway
1. Push to GitHub
2. Connect repo on railway.app
3. Add environment variable: `DATABASE_URL` (PostgreSQL from Railway)
4. Add `SECRET_KEY`
5. Deploy!

## Deploy to Replit
1. Upload project
2. Set Secrets: `SECRET_KEY`, `DATABASE_URL`
3. Run `python app.py`

## Tech Stack
- Flask + SQLAlchemy + Flask-Login
- SQLite (local) / PostgreSQL (production)
- Chart.js for analytics
- Vanilla JS + CSS (no heavy frameworks)

## KTU Grading Scale
| Grade | Marks | Points |
|-------|-------|--------|
| S | 90–100 | 10 |
| A+ | 80–89 | 9 |
| A | 70–79 | 8 |
| B+ | 60–69 | 7 |
| B | 50–59 | 6 |
| C | 45–49 | 5 |
| D | 40–44 | 4 |
| F | <40 | 0 |

Built for Rang @ TKM College of Engineering 🎓
