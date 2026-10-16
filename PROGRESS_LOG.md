# Project progress log

## Complete implementation

- Built the seven-table SQLite model, foreign-key enforcement, schema migration,
  cached connection, and idempotent Data Analyst seed.
- Replaced temporary data and calculations with database-backed profile,
  assessment, career, ordered recommendation, roadmap, resource, progress,
  dashboard, and study-planner flows.
- Added install/run instructions, database and progress formula documentation,
  and a short viva walkthrough.
- Verification: `python -m pytest tests/` passes (45 tests); the Streamlit app
  rendered the profile, Data Analyst roadmap/resources, progress, dashboard,
  and planner screens during a local browser smoke test. The schema migration
  test confirmed legacy skill/resource progress is preserved and only the
  seven target tables remain.
- Pending: compare with official ER diagram/Data Dictionary if supplied; this
  implementation uses the master prompt's default because those documents were
  not included.
- Open assumptions: the app uses one selected active student profile without
  authentication; study hours are split evenly across remaining skills.

## Career catalog and resume builder

- Added five more ordered career paths with role-specific skills and learning
  resources; career options remain database-backed and seed insertion is safe
  to repeat.
- Added the `resume_profiles` supporting table for earlier resume data.
- Verification at the time: pending the updated test suite and UI smoke test.

## Current workflow and UI polish

- Resume Builder is now upload-first: PDF/DOCX/TXT review, target-career skill
  comparison, recommendations, editable formatting, and DOCX/Markdown exports.
  Upload text is session-only and is not written to the database.
- Update Progress is read-only and calculated from the student's saved
  current-skills assessment; manual progress sliders have been removed.
- Career assessment shows skills for the selected path and preserves previously
  assessed transferable skills when switching paths.
- Added consistent shared responsive styling and sidebar step progress;
  dashboard metrics now distinguish completed skills, remaining skills, and
  next recommended skill.
- Verification: `python -m pytest -q` and screen smoke tests pass; see the
  current test output for the verified count.
