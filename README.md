# Personalized Education Path Generator

A local-first Streamlit learning companion that starts with an uploaded resume,
compares its evidence with supported career profiles, and builds an ordered
learning roadmap with transparent study-time estimates and YouTube channel
recommendations. Students can also use the existing career-selection, progress,
planner, and resume-review workflows.

## Technology

- Python 3.10+
- Streamlit 1.49+ for the local desktop-style interface
- SQLite for persistent application data
- pytest for automated tests
- Requests for optional OpenAI and YouTube Data API calls

Pandas and NumPy are not used because the current data is small and ordinary
Python collections and SQLite queries are clearer for this project.

## Features

- Create and select a student profile; no login or authentication.
- Select from six seeded career paths: Data Analyst, Frontend Developer,
  Backend Developer, Data Scientist, UI/UX Designer, and Cybersecurity Analyst.
- Assess known skills and follow a career-specific, dependency-ordered path.
- Compare current skills with required skills in the career's dependency order.
- Recommend the earliest incomplete skill and show the future steps and learning
  resources.
- View automatically calculated progress from skills marked as already known
  during the current-skills assessment; the progress screen is read-only.
- Review overall progress, current focus, completed and remaining skills, and
  recent updates on the dashboard.
- Split available weekly study hours evenly across the ordered skill gap.
- Upload an existing PDF, DOCX, or TXT resume for rule-based section and
  achievement feedback. Review is targeted to one of the available careers
  and compares listed skills with the uploaded document. Uploaded document
  text is processed in the active app session only; it is not stored in SQLite.
- Start from **Resume Career Path** to identify resume-backed skills and compare
  proficiency against six supported profiles: Data Analyst, Frontend Developer,
  Backend Developer, Data Scientist, UI/UX Designer, and Cybersecurity Analyst.
  These are the only roles currently matched; this is not a complete job-market
  search.
- See role matches scored by evidence level and role requirements, then choose
  a role for an ordered path toward practical entry-level skill proficiency.
- Estimate study hours and a range of weeks at the student's chosen pace.
  Estimates are planning guidance, not promised completion dates.
- Find YouTube **channels only** for each roadmap skill on demand. Without a
  YouTube API key, the app provides clearly labeled curated channel suggestions.
- Optionally enable AI resume interpretation and learning-hour estimates using
  OpenAI. AI is opt-in; common email addresses, phone numbers, and URLs are
  redacted before a request. Other personal details may remain. Provider data
  handling depends on the account's retention settings. Resume text is not
  stored by the app.

## Project structure

```text
app.py                 Streamlit app entry point
database/              SQLite connection, schema, migrations, and seed data
modules/               Profile, career, assessment, roadmap, and resume-analysis logic
ui/                    Streamlit screens
tests/                 pytest coverage
docs/                  Progress log and viva demonstration guide
data/                  Created automatically; local SQLite database
```

## Database

SQLite is the source of truth. The seven core learning-path tables are
`students`, `careers`, `skills`, `career_skills`, `roadmaps`, `progress`, and
`resources`. A `resume_profiles` table remains in the schema for compatibility
with existing local data, but the upload-based resume review does not write
uploaded content to it.
`career_skills.sequence_order` controls the recommendation and roadmap order.
Every connection explicitly enables SQLite foreign-key enforcement. The schema
and six-career catalog are initialized idempotently when the app starts; the
database file is created if it does not exist.

Overall roadmap progress is:

```text
round(100 * completed_skill_count / total_required_skill_count)
```

It counts completed required skills, not partially completed percentages.
Per-skill progress is independently stored from 0 to 100; a skill is completed
only at 100%.

## Install and run

From the project root:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit (normally
`http://localhost:8501`). The app creates the SQLite database and seed rows on
first launch. To initialize explicitly:

```powershell
python -c "from database.seed import seed_db; seed_db()"
```

Run tests with:

```powershell
python -m pytest tests/
```

## Example workflow

1. In **Resume Career Path**, upload a resume and inspect the evidence-backed
   matches among the supported profiles.
2. Choose a role to review the ordered learning path, estimated time, and
   on-demand YouTube channel recommendations.
3. Optionally create a student profile and use the existing career-selection
   workflows to assess skills and track progress.
4. Review the automatically calculated completed/missing skills on Update
   Progress. To revise what you already know, update the current-skills
   assessment under Select Career.
5. Review progress and recent activity on Dashboard, or allocate weekly hours
   in Study Planner.
6. In Resume Builder, upload an existing PDF, DOCX, or TXT resume, choose a
   target career, and review its sections, role-related skills, and practical
   improvement suggestions.

The role hint on Resume Career Path breaks otherwise-equal matches only; it does
not create resume evidence or change the evidence-based fit score.

## Optional API configuration

Local matching and curated YouTube suggestions work without API keys. To enable
the optional providers, set server-side environment variables before launching:

```powershell
$env:OPENAI_API_KEY = "your-server-side-key"
$env:OPENAI_MODEL = "gpt-4o-mini"
$env:YOUTUBE_API_KEY = "your-server-side-key"
python -m streamlit run app.py
```

The OpenAI key is used only after a student checks the explicit consent box.
Requests use structured output and `store: false`; this does not mean zero
provider retention. Review your OpenAI account's data controls before enabling
AI for student resumes. Provider errors are reported and students can retry
with local matching. Learning-time estimates are labeled with their source.

The YouTube Data API is called only after a student requests channels for an
individual roadmap skill. It searches channels, not videos, and receives no
resume content. Each request consumes API quota; curated suggestions work
without a key.

The Data Analyst path is ordered as SQL, Excel, Statistics, Python, Pandas,
Data Visualization, and Data Analysis Project.

Each career has its own saved skill sequence and learning links. Skills such as
Python, SQL, and Git are shared between paths because they are useful in more
than one role; progress for a shared skill can therefore carry over to another
selected career.

## Viva explanations

- **Skill gap:** The system compares skills known by the student with the skills
  required for the selected career and identifies incomplete skills.
- **Recommendation:** The next incomplete skill is selected by its saved
  `sequence_order`; this is deterministic rule-based logic, not AI.
- **Roadmap:** The ordered skill gap becomes a numbered learning path with
  resources attached to each skill.
- **Progress formula:** Completed required skills divided by all required skills,
  multiplied by 100 and rounded to the nearest whole percent.
- **SQLite:** SQLite stores profiles, careers, skills, roadmaps, progress, and
  resources locally in one file.
- **No login:** This is a single-profile desktop tool; a simple selector chooses
  the active student instead of adding authentication.
- **Resume review:** The student uploads an existing resume and gets
  deterministic feedback for the selected career; uploaded documents are not
  stored by the app.
- **Uploaded resume review:** PDF/DOCX/TXT text is reviewed with deterministic
  checks for common sections, contact details, bullets, action verbs, and
  measurable outcomes, plus a comparison against target-career skills.
  Formatting preserves the supplied facts and does not generate credentials
  or experience.

## Future scope

The app currently matches only six local role profiles; broader, location-aware
job-market matching would require a licensed occupational dataset and additional
validation. Authentication and cloud resume storage are not implemented.
