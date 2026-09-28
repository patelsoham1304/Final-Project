ROLE: Act as a Senior Streamlit Frontend Developer with 20+ years of experience 
in production-grade Python applications. Write clean, well-commented, 
professional code — this is a college BCA final year project but should 
follow real industry standards.

ACTIVE SKILLS FOR THIS TASK: ponytail, superpower, caveman
(Use these 3 skills throughout this task for efficient coding as configured 
in this agent.)

PROJECT: Personalized Education Path Generator
TEAM SIZE: 3 members (you are building the UI layer only)
DEADLINE: 3 days
STACK: Python 3.10+, Streamlit
CONSTRAINT: No business logic and no raw SQL allowed in this layer.

===========================================================
FILES YOU OWN (create/modify ONLY these):
===========================================================
ui/__init__.py
ui/dashboard.py
ui/profile_ui.py
ui/career_ui.py
ui/roadmap_ui.py
ui/progress_ui.py
ui/planner_ui.py
app.py

===========================================================
CRITICAL DEPENDENCY-SAFETY RULES (must follow strictly):
===========================================================
1. Only import from modules/, NEVER directly from database/.
   Correct:
     from modules.skill_gap import calculate_skill_gap
     from modules.roadmap import generate_roadmap
   Wrong:
     from database.models import Student   # NEVER do this in ui/

   Reason: skipping the business-logic layer breaks the UI → modules → 
   database dependency chain and will cause integration conflicts with 
   the other two team members' code.

2. `streamlit run app.py` must succeed from the project root at every 
   single step of development. Test this after every change you make — 
   do not batch untested changes.

3. NEVER duplicate calculate_skill_gap(), generate_roadmap(), or 
   calculate_overall_progress() logic inside any ui/*.py file — not even 
   for a "quick preview." Always call the real modules/ function.

4. Use st.session_state carefully, and ONLY inside ui/*.py files. Never 
   let session state handling leak into modules/ or database/.

5. If modules/ isn't ready yet, build every screen against these AGREED 
   function signatures using temporary sample return values. Mark every 
   mock clearly with the comment `# TEMP UI MOCK` so it's easy to find 
   and remove once modules/ is integrated:

   calculate_skill_gap(student_id: str, current_skills: list, target_career: str) -> dict
   get_next_recommended_skill(student_id: str, target_career: str) -> dict
   generate_roadmap(student_id: str, target_career: str, current_skills: list) -> dict
   calculate_overall_progress(student_id: str) -> dict

6. Wrap every call to a modules/ function in try/except. On failure, show 
   a friendly st.error() or st.warning() message — NEVER let a raw Python 
   traceback reach the UI.

===========================================================
WORKFLOW TO BUILD (in this exact order):
===========================================================
Create Student → Select Career → Select Current Skills → Show Skill Gap →
Show Recommendation → Show Roadmap → Show Resources → Update Progress →
Dashboard

Each screen should be its own function in the appropriate ui/*.py file, 
routed from app.py using a single source of truth in 
st.session_state.workflow_step (or equivalent), so navigation between 
screens is centralized and easy to extend.

===========================================================
GIT / COMMIT CONVENTIONS:
===========================================================
Branch: feature/ui
Commit style: feat: ..., test: ..., fix: ...
Make small, atomic commits per screen/feature, not one giant commit.

===========================================================
BEFORE ANY MERGE — VERIFY:
===========================================================
- `streamlit run app.py` runs end-to-end with zero import errors
- Zero "missing function" errors even when modules/ isn't ready 
  (TEMP UI MOCK should silently cover the gap)
- Full workflow (Create Student → Dashboard) completes without a crash
- No raw tracebacks appear anywhere in the browser UI
- No file outside the "FILES YOU OWN" list was created or modified

===========================================================
OUTPUT FORMAT:
===========================================================
- Generate the files one at a time, in the workflow order listed above
- After each file, briefly state what TEMP UI MOCKS were used and which 
  real modules/ function will eventually replace them
- End with a short manual test checklist I can run screen-by-screen