# 🚀 Personalized Education Path Generator - Quick Start Guide

## Project Status
✅ **READY TO RUN** - All features working, 52 tests passing, fully functional.

## What's Included

### 🎯 Features
- **6 Career Paths**: Data Analyst, Frontend Developer, Backend Developer, Data Scientist, UI/UX Designer, Cybersecurity Analyst
- **Profile Management**: Create and manage student profiles
- **Career Selection**: Choose from 6 industry-recognized career paths
- **Skill Gap Analysis**: Identify skills to learn for your chosen career
- **Learning Roadmap**: Structured path with ordered skills and resources
- **Progress Tracking**: Monitor skill completion (0-100%)
- **Smart Study Planner**: AI-powered personalized learning schedule
- **Resume Builder**: Create professional Markdown resumes with completed skills
- **Interactive Dashboard**: Visual progress tracking with charts

### 📊 Database
- SQLite database persists across sessions
- Automatic schema initialization and migrations
- Legacy data compatibility built-in

## How to Run

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the App
```bash
python -m streamlit run app.py
```

**Or use the launcher script:**
```bash
python run_app.py
```

### Step 3: Open in Browser
Streamlit will automatically open your browser at:
```
http://localhost:8501
```

If not, manually navigate to that URL.

## App Workflow

1. **Create Student** - Enter your name and email
2. **Select Career** - Choose from 6 career paths (Data Analyst, Frontend Developer, etc.)
3. **Skill Gap & Roadmap** - View required skills and create a learning roadmap
4. **Update Progress** - Track your skill learning (in_progress, completed, etc.)
5. **Study Planner** - Get AI-generated personalized study schedule
6. **Resume Builder** - Create a professional Markdown resume from your profile and completed skills
7. **Dashboard** - Visual overview of your progress with charts and stats

## Resume Builder Features
- Edit resume headline, summary, education, projects, certifications
- Add portfolio and LinkedIn URLs (with validation)
- Auto-include completed skills in resume
- Download as clean Markdown file
- Professional formatting ready for word processors

## Testing

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_resume.py -v
```

**Current Test Status**: ✅ 52/52 tests passing
- test_database.py: 10 tests
- test_planner.py: 5 tests  
- test_progress.py: 11 tests
- test_recommendation.py: 5 tests
- test_resume.py: 7 tests
- test_roadmap.py: 6 tests
- test_skill_gap.py: 8 tests

## Project Structure

```
.
├── app.py                 # Main Streamlit entry point
├── database/
│   ├── schema.py         # SQLite schema & migrations
│   ├── db.py             # Database operations (CRUD)
│   ├── seed.py           # Initial data: 6 careers, 40+ skills
│   └── __init__.py       # Exports
├── modules/
│   ├── resume.py         # Resume validation & Markdown export
│   ├── recommendation.py # Career/skill recommendations
│   ├── planner.py        # AI study schedule generator
│   ├── skill_gap.py      # Skill gap analysis
│   └── progress.py       # Progress tracking logic
├── ui/
│   ├── resume_ui.py      # Resume editor UI (new)
│   ├── profile_ui.py     # Student profile UI
│   ├── career_ui.py      # Career selection UI
│   ├── roadmap_ui.py     # Roadmap & skill gap UI
│   ├── progress_ui.py    # Progress tracker UI
│   ├── planner_ui.py     # Study planner UI
│   └── dashboard.py      # Dashboard with charts
├── tests/
│   ├── test_database.py      # 10 tests
│   ├── test_resume.py        # 7 new tests
│   ├── test_planner.py       # 5 tests
│   ├── test_progress.py      # 11 tests
│   ├── test_recommendation.py# 5 tests
│   ├── test_roadmap.py       # 6 tests
│   └── test_skill_gap.py     # 8 tests
├── data/
│   └── education_path.db # SQLite database (auto-created)
├── requirements.txt      # Dependencies
└── README.md            # Full documentation
```

## Key Components Explained

### Career Catalog (database/seed.py)
Each of the 6 careers includes:
- Ordered skill progression (foundational → advanced)
- Shared skills across paths (Python, SQL, Git transfer between roles)
- Role-specific resources (videos, courses, docs, articles)

### Resume Builder (modules/resume.py + ui/resume_ui.py)
- Validates URLs (no spaces, proper http/https)
- Exports clean Markdown with completed skills
- One-to-one persistence per student
- Auto-populated from study progress

### Database Persistence
- Automatic schema creation on first run
- Foreign key constraints for data integrity
- Cascade deletes for cleanup
- Text timestamps (SQLite native support)

## Troubleshooting

### "Database could not be initialized"
- Ensure the `data/` folder has write permissions
- Check that `.git` folder exists (project structure)

### Port 8501 already in use
- Kill the existing Streamlit process
- Or specify a different port:
  ```bash
  streamlit run app.py --server.port 8502
  ```

### Import errors
- Reinstall dependencies:
  ```bash
  pip install --force-reinstall -r requirements.txt
  ```

### Tests fail
- Clear pytest cache:
  ```bash
  rm -rf .pytest_cache
  pytest tests/ -v
  ```

## Next Steps

After running the app:
1. Create a new student profile
2. Select a career path
3. Review recommended skills
4. Start tracking progress
5. Build your resume
6. Use the dashboard to visualize learning journey

Enjoy your personalized learning path! 🎓
