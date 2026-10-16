# Five-minute viva demonstration

1. **Create Student (30 seconds):** Create a profile or select a saved student.
   Explain that profiles and progress are stored in local SQLite; the selector
   is not a login system.
2. **Select Career (45 seconds):** Choose Data Analyst and mark a few known
   skills. Explain that the options come from the database, not a UI mock list.
3. **Skill Gap & Roadmap (60 seconds):** Show known skills, missing skills, the
   next recommendation, dependency-ordered future skills, and a resource link.
   Explain that `career_skills.sequence_order` controls the order.
4. **Update Progress (45 seconds):** Show the read-only completed and
   still-to-learn skill checklist. Explain that completion is derived from the
   saved current-skills assessment and the percentage is completed career skills
   divided by required career skills. Reassess known skills under Select Career.
5. **Dashboard (45 seconds):** Show completed and remaining skills, current
   focus, roadmap preview, resources, and recent updates. Explain the overall
   formula: completed required skills / all required skills * 100, rounded to
   the nearest whole percent.
6. **Study Planner (30 seconds):** Enter weekly study hours and show the even
   split across the remaining skills in their saved order.
7. **Resume Builder (60 seconds):** Upload a PDF, DOCX, or TXT resume, select a
   target role, review the checklist and skill feedback, edit the polished
   version, and download it as DOCX or Markdown. Explain that uploads are not
   saved to the app database and that it does not invent qualifications.

## Plain-language module explanations

- **Skill gap:** Compares what the student knows with the skills required by the
  selected career.
- **Recommendation:** Chooses the earliest incomplete skill by its saved order.
- **Roadmap:** Presents the ordered missing skills as numbered learning steps.
- **SQLite:** Stores student, career, skill, roadmap, progress, and resource
  data locally so it survives refreshes and restarts.
