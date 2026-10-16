"""PDF Roadmap Generator using ReportLab or clean printable HTML document."""

from __future__ import annotations

import io
import datetime

def generate_roadmap_html(
    student_name: str,
    career_name: str,
    overall_progress: float,
    known_skills: list[str],
    remaining_steps: list[dict],
    student_email: str = "",
) -> str:
    """Generate a clean, high-resolution printable HTML document ready for PDF printing/saving."""
    today_str = datetime.date.today().strftime("%B %d, %Y")
    
    known_html = "".join(
        f'<span style="display:inline-block;background:#ecfdf5;color:#065f46;border:1px solid #a7f3d0;padding:4px 10px;border-radius:6px;font-size:12px;margin:3px 4px 3px 0;font-weight:600;">✓ {s}</span>'
        for s in known_skills
    ) if known_skills else '<span style="color:#64748b;font-size:12px;font-style:italic;">No pre-existing skills recorded</span>'

    steps_html = ""
    for step in remaining_steps:
        s_num = step.get("step", 1)
        s_name = step.get("skill", "")
        steps_html += f"""
        <div style="display:flex;align-items:center;padding:10px 14px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;margin-bottom:8px;">
            <div style="width:28px;height:28px;border-radius:50%;background:#0284c7;color:#ffffff;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:12px;margin-right:12px;">
                {s_num}
            </div>
            <div style="flex:1;">
                <div style="font-weight:700;color:#0f172a;font-size:14px;">{s_name}</div>
                <div style="font-size:11px;color:#64748b;">Target milestone for {career_name}</div>
            </div>
            <span style="font-size:11px;background:#e0f2fe;color:#0369a1;padding:2px 8px;border-radius:12px;font-weight:600;">To Learn</span>
        </div>
        """

    if not steps_html:
        steps_html = '<div style="padding:14px;background:#ecfdf5;color:#047857;border-radius:8px;font-weight:600;">🎉 Congratulations! You have mastered all skills required for this career path!</div>'

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{student_name} - {career_name} Roadmap</title>
    <style>
        @page {{ size: A4; margin: 20mm; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #1e293b;
            background: #ffffff;
            line-height: 1.5;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }}
        .header {{
            border-bottom: 2px solid #0284c7;
            padding-bottom: 16px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }}
        .brand {{
            font-size: 24px;
            font-weight: 900;
            color: #0284c7;
            letter-spacing: -0.5px;
        }}
        .tagline {{
            font-size: 12px;
            color: #64748b;
        }}
        .section-title {{
            font-size: 14px;
            font-weight: 800;
            color: #0f172a;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin: 20px 0 10px 0;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 4px;
        }}
        .progress-bar-wrap {{
            background: #e2e8f0;
            height: 10px;
            border-radius: 5px;
            overflow: hidden;
            margin: 8px 0;
        }}
        .progress-bar-fill {{
            background: #0284c7;
            height: 100%;
            width: {int(overall_progress)}%;
            border-radius: 5px;
        }}
        .footer {{
            margin-top: 36px;
            padding-top: 14px;
            border-top: 1px dashed #cbd5e1;
            font-size: 11px;
            color: #94a3b8;
            text-align: center;
        }}
        @media print {{
            .no-print {{ display: none; }}
            body {{ padding: 0; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div class="brand">PathFinder AI 🎯</div>
            <div class="tagline">Personalized Educational Roadmap & Career Plan</div>
        </div>
        <div style="text-align: right; font-size: 12px; color: #64748b;">
            <div><b>Issued Date:</b> {today_str}</div>
            <div><b>Learner:</b> {student_name}</div>
        </div>
    </div>

    <div style="background: #f0f9ff; border: 1.5px solid #bae6fd; border-radius: 12px; padding: 18px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 12px; text-transform: uppercase; font-weight: 700; color: #0284c7;">Target Career Path</div>
                <div style="font-size: 22px; font-weight: 800; color: #0f172a;">{career_name}</div>
                <div style="font-size: 12px; color: #475569;">Email: {student_email or 'Registered Student'}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 26px; font-weight: 900; color: #0284c7;">{int(overall_progress)}%</div>
                <div style="font-size: 11px; font-weight: 700; color: #64748b;">COMPLETED</div>
            </div>
        </div>
        <div class="progress-bar-wrap">
            <div class="progress-bar-fill"></div>
        </div>
    </div>

    <div class="section-title">Already Acquired Skills ({len(known_skills)})</div>
    <div style="margin-bottom: 16px;">
        {known_html}
    </div>

    <div class="section-title">Step-by-Step Learning Roadmap ({len(remaining_steps)} steps remaining)</div>
    <div style="margin-bottom: 20px;">
        {steps_html}
    </div>

    <div class="footer">
        Generated automatically by PathFinder AI Learning System · Valid for academic & career preparation tracking.
    </div>
</body>
</html>
"""
    return html_content


def generate_roadmap_pdf_or_docx(
    student_name: str,
    career_name: str,
    overall_progress: float,
    known_skills: list[str],
    remaining_steps: list[dict],
) -> bytes:
    """Fallback generator to produce a clean printable DOCX document containing the complete roadmap."""
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Title Header
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = title.add_run(f"PathFinder AI - Career Roadmap")
    r_title.bold = True
    r_title.font.size = Pt(20)
    r_title.font.color.rgb = RGBColor(2, 132, 199)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = sub.add_run(f"Target Career: {career_name} | Learner: {student_name}")
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph(f"Overall Progress: {int(overall_progress)}% Completed\n")

    # Known Skills
    h_known = doc.add_paragraph()
    r_hk = h_known.add_run("✓ Already Acquired Skills:")
    r_hk.bold = True
    r_hk.font.size = Pt(13)
    if known_skills:
        for s in known_skills:
            doc.add_paragraph(f"• {s}", style="List Bullet")
    else:
        doc.add_paragraph("• None recorded")

    # Roadmap Steps
    doc.add_paragraph("")
    h_steps = doc.add_paragraph()
    r_hs = h_steps.add_run("🎯 Ordered Learning Steps:")
    r_hs.bold = True
    r_hs.font.size = Pt(13)

    if remaining_steps:
        for step in remaining_steps:
            doc.add_paragraph(f"Step {step.get('step', 1)}: {step.get('skill', '')}", style="List Bullet")
    else:
        doc.add_paragraph("🎉 All curriculum skills completed!")

    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()
