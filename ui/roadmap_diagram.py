"""Build and render a self-contained, data-backed career roadmap diagram."""

from __future__ import annotations

import base64
import json
from urllib.parse import urlparse

import streamlit.components.v1 as components


_CAREER_GROUPS = {
    "Data Analyst": [
        ("Data Foundations", ("SQL", "Excel", "Statistics")),
        ("Analysis Tools", ("Python", "Pandas")),
        ("Insights & Practice", ("Data Visualization", "Data Analysis Project")),
    ],
    "Frontend Developer": [
        ("Web Foundations", ("HTML", "CSS", "JavaScript")),
        ("Workflow & Layout", ("Git", "Responsive Design")),
        ("Interfaces & Practice", ("React", "Frontend Project")),
    ],
    "Backend Developer": [
        ("Language & Workflow", ("Python", "Git")),
        ("Data & APIs", ("SQL", "HTTP and REST APIs")),
        ("Engineering Practice", ("Backend Development", "Software Testing")),
        ("Build a Project", ("Backend Project",)),
    ],
    "Data Scientist": [
        ("Programming Foundations", ("Python", "Statistics", "SQL")),
        ("Data Preparation", ("NumPy", "Pandas")),
        (
            "Modeling & Communication",
            ("Data Visualization", "Machine Learning Fundamentals", "Data Science Project"),
        ),
    ],
    "UI/UX Designer": [
        ("Design Foundations", ("Design Principles", "User Research")),
        ("Prototyping", ("Wireframing", "Figma", "Prototyping")),
        ("Accessible Design", ("Accessibility",)),
        ("Portfolio Practice", ("UX Portfolio Project",)),
    ],
    "Cybersecurity Analyst": [
        ("System Foundations", ("Networking Fundamentals", "Linux Command Line", "Python")),
        ("Security Fundamentals", ("Web Security Fundamentals", "OWASP Top 10")),
        ("Monitoring & Practice", ("Security Monitoring", "Cybersecurity Lab Project")),
    ],
}


def _safe_http_url(value):
    """Allow only web links in the embedded diagram."""
    if not isinstance(value, str) or not value.strip():
        return None
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return value.strip()


def build_roadmap_diagram_data(
    career_name, required_skills, assessed_by_skill_id, resources_by_skill_id
):
    """Map assessed career skills to full, ordered roadmap branches."""
    if not isinstance(career_name, str) or not career_name.strip():
        raise ValueError("A career name is required to build the roadmap diagram.")
    if not required_skills:
        raise ValueError("At least one required skill is needed for the roadmap diagram.")

    known_skill_ids = {
        skill["id"]
        for skill in required_skills
        if (saved := assessed_by_skill_id.get(skill["id"]))
        and saved["status"] == "completed"
    }
    ordered_skills = list(required_skills)
    nodes = [
        {
            "id": "career-root",
            "label": career_name.strip(),
            "type": "root",
            "parentId": None,
            "status": "none",
            "description": f"Ordered learning path for {career_name.strip()}.",
        }
    ]
    skills_by_name = {skill["name"]: skill for skill in ordered_skills}
    groups = _CAREER_GROUPS.get(career_name.strip(), [])
    assigned = set()
    normalized_groups = []
    for label, names in groups:
        matching = [name for name in names if name in skills_by_name and name not in assigned]
        if matching:
            normalized_groups.append((label, matching))
            assigned.update(matching)

    ungrouped = [
        skill["name"] for skill in ordered_skills if skill["name"] not in assigned
    ]
    for offset in range(0, len(ungrouped), 3):
        group_number = len(normalized_groups) + 1
        normalized_groups.append(
            (
                "Additional Skills" if not normalized_groups else f"Further Skills {group_number}",
                ungrouped[offset : offset + 3],
            )
        )

    for group_index, (label, group_skills) in enumerate(normalized_groups, start=1):
        group_id = f"group-{group_index}"
        nodes.append(
            {
                "id": group_id,
                "label": label,
                "type": "branch",
                "parentId": "career-root",
                "status": "none",
                "description": f"Learning area {group_index}: {label}.",
                "sequence": group_index,
            }
        )
        for name in group_skills:
            skill = skills_by_name[name]
            saved = assessed_by_skill_id.get(skill["id"])
            status = "known" if skill["id"] in known_skill_ids else "to_learn"
            resources = resources_by_skill_id.get(skill["id"], [])
            resource_url = next(
                (
                    url for resource in resources
                    if (url := _safe_http_url(resource["url"]))
                ),
                None,
            )
            node = {
                "id": f"skill-{skill['id']}",
                "label": skill["name"],
                "type": "skill",
                "parentId": group_id,
                "status": status,
                "description": skill["description"],
                "sequence": next(
                    index for index, item in enumerate(required_skills, start=1)
                    if item["id"] == skill["id"]
                ),
            }
            if resource_url:
                node["url"] = resource_url
            nodes.append(node)
    return {
        "nodes": nodes,
        "skillCount": len(ordered_skills),
        "totalSkillCount": len(required_skills),
        "knownSkillCount": len(known_skill_ids),
    }


def build_resume_roadmap_diagram_data(
    career_name, required_skill_names, assessed_skills, roadmap_steps
):
    """Adapt resume-assessed skill levels and estimates to the shared diagram."""
    if not isinstance(required_skill_names, list) or not required_skill_names:
        raise ValueError("At least one required skill is needed for the roadmap diagram.")

    level_by_name = {
        item["name"]: max(0, min(int(item["level"]), 5))
        for item in assessed_skills
        if isinstance(item, dict)
        and item.get("name") in required_skill_names
        and isinstance(item.get("level"), int)
        and not isinstance(item.get("level"), bool)
    }
    step_by_name = {step["skill"]: step for step in roadmap_steps}
    required_skills = []
    assessed_by_id = {}
    for skill_id, name in enumerate(required_skill_names, start=1):
        level = level_by_name.get(name, 0)
        step = step_by_name.get(name)
        description = (
            f"Resume evidence level {level}/5; working target is level 3/5."
        )
        if step:
            description += (
                f" Estimated learning time: {step['estimated_hours']} hours, "
                f"weeks {step['start_week']}–{step['end_week']}."
            )
        required_skills.append(
            {"id": skill_id, "name": name, "description": description}
        )
        assessed_by_id[skill_id] = {
            "status": "completed" if level >= 3 else "not_started",
        }
    return build_roadmap_diagram_data(
        career_name,
        required_skills,
        assessed_by_id,
        {},
    )


def _roadmap_html(data):
    encoded_data = base64.b64encode(
        json.dumps(data, ensure_ascii=True).encode("utf-8")
    ).decode("ascii")
    return _HTML.replace("__ROADMAP_DATA__", encoded_data)


def roadmap_diagram_height(skill_count, group_count=None):
    """Size the viewport automatically to fit the diagram content without excess blank space."""
    if isinstance(skill_count, bool) or not isinstance(skill_count, int) or skill_count < 0:
        raise ValueError("Skill count must be a non-negative integer.")
    if group_count is None:
        group_count = max(1, (skill_count + 2) // 3)
    if isinstance(group_count, bool) or not isinstance(group_count, int) or group_count < 0:
        raise ValueError("Group count must be a non-negative integer.")
    # Dynamic height: header (120px) + each branch group (95px) + comfortable bottom margin (60px)
    return max(420, 120 + group_count * 95 + 60)


def render_roadmap_diagram(data):
    """Embed the interactive diagram without network access or persistent storage."""
    skill_count = data.get("skillCount", sum(node.get("type") == "skill" for node in data["nodes"]))
    group_count = sum(node.get("type") == "branch" for node in data["nodes"])
    components.html(
        _roadmap_html(data),
        height=roadmap_diagram_height(skill_count, group_count),
        scrolling=False,
    )


_HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box}html,body{width:100%;height:100%;margin:0}body{display:flex;flex-direction:column;background:#0b1024;color:#f8fafc;font:14px/1.4 'Inter',system-ui,-apple-system,"Segoe UI",sans-serif}
.bar{position:sticky;top:0;z-index:4;display:flex;gap:12px;align-items:center;padding:10px 16px;background:#111833;border-bottom:1px solid rgba(255,255,255,0.08)}
.bar strong{margin-right:auto;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:750;font-size:15px;color:#f8fafc}
.bar input{width:min(35%,220px);height:34px;padding:0 10px;border:1px solid rgba(255,255,255,0.14);border-radius:8px;background:#0e152e;color:#fff;font:inherit;outline:0}
.bar input:focus{border-color:#f59e0b;box-shadow:0 0 0 3px rgba(245,158,11,0.25)}
.bar button{height:34px;padding:0 12px;border:1px solid rgba(245,158,11,0.4);border-radius:8px;background:rgba(245,158,11,0.12);color:#fbbf24;font:650 12px system-ui;cursor:pointer;transition:all .2s}
.bar button:hover{background:rgba(245,158,11,0.25);border-color:#f59e0b}
.meter-label{padding:6px 16px 4px;color:#94a3b8;font-size:12px;display:flex;gap:14px;align-items:center;background:#0d132b}
.view{position:relative;flex:1;overflow:hidden;cursor:grab;touch-action:none;background:radial-gradient(rgba(45,60,110,0.5) 1px,transparent 1px) 0 0/22px 22px,#0b1024}
.view.drag{cursor:grabbing}
.world{position:absolute;top:0;left:0;right:0;width:100%;transform-origin:50% 0}
.root{position:relative;z-index:1;display:flex;justify-content:center;padding:16px 0 20px}
.root button{min-width:min(260px,70%);padding:10px 20px;border:2px solid #f59e0b;border-radius:12px;background:linear-gradient(135deg,rgba(245,158,11,0.22),rgba(217,119,6,0.1));color:#ffffff;font:750 16px/1.2 system-ui;box-shadow:0 0 20px rgba(245,158,11,0.25);cursor:pointer;transition:all .2s}
.area-title{min-width:140px;max-width:190px;min-height:38px;font-size:13px;text-align:center;flex:0 0 auto;padding:7px 14px;border:1.5px solid rgba(59,130,246,0.5);border-radius:8px;background:#131c3b;color:#93c5fd;font-weight:650;box-shadow:0 4px 12px rgba(0,0,0,0.3);cursor:pointer;transition:all .2s}
.areas{position:relative;z-index:1;padding:0 14px 24px;width:100%;max-width:860px;margin:0 auto}
.area{position:relative;display:grid;grid-template-columns:1fr 1fr;align-items:center;min-height:76px;margin-bottom:14px}
.area-inner{display:flex;width:100%;align-items:center;gap:14px;padding:4px 10px}
.area[data-side="right"] .area-inner{grid-column:2;justify-content:flex-start}
.area[data-side="left"] .area-inner{grid-column:1;flex-direction:row-reverse;justify-content:flex-start}
.skill-group{display:flex;flex-wrap:wrap;gap:6px;align-items:center;flex:1;min-width:0}
.area[data-side="left"] .skill-group{justify-content:flex-end}
.skill{flex:0 1 auto;min-width:85px;max-width:175px;min-height:36px;padding:6px 12px;border:1px solid rgba(255,255,255,0.12);border-radius:8px;background:#172247;color:#f1f5f9;font:600 12px system-ui;box-shadow:0 3px 8px rgba(0,0,0,0.3);text-align:center;cursor:pointer;transition:all .2s}
.skill:hover,.area-title:hover,.root button:hover{outline:2px solid #f59e0b;box-shadow:0 6px 16px rgba(245,158,11,0.3);transform:translateY(-2px)}
.skill.dim{opacity:.18}.skill.match{outline:2.5px solid #f59e0b;box-shadow:0 0 16px #f59e0b88}
.check{position:absolute;top:50%;right:-9px;display:grid;width:19px;height:19px;place-items:center;border:2px solid #0b1024;border-radius:50%;background:#3b82f6;color:white;font:900 11px system-ui;transform:translateY(-50%);box-shadow:0 0 8px rgba(59,130,246,0.6)}
.check.known{background:#10b981;box-shadow:0 0 8px rgba(16,185,129,0.7)}
.area[data-side="left"] .area-title .check,.area[data-side="left"] .skill .check{right:auto;left:-9px}
.svg{position:absolute;inset:0;z-index:0;overflow:visible;pointer-events:none}
.solid{fill:none;stroke:#f59e0b;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 8px rgba(245,158,11,0.55));transition:stroke 0.3s ease}
.dotted{fill:none;stroke:#3b82f6;stroke-width:2;stroke-linecap:round;stroke-dasharray:4 7;animation:dashFlow 20s linear infinite;filter:drop-shadow(0 0 6px rgba(59,130,246,0.5))}
@keyframes dashFlow {
  to {
    stroke-dashoffset: -1000;
  }
}
.root button{min-width:min(260px,70%);padding:10px 20px;border:2px solid #f59e0b;border-radius:12px;background:linear-gradient(135deg,rgba(245,158,11,0.25),rgba(217,119,6,0.12));color:#ffffff;font:750 16px/1.2 system-ui;box-shadow:0 0 24px rgba(245,158,11,0.3);cursor:pointer;transition:all .3s cubic-bezier(0.16,1,0.3,1);animation:pulse-glow 3s infinite ease-in-out}
.tip{position:fixed;z-index:9;display:none;max-width:280px;padding:12px 15px;border:1px solid rgba(245,158,11,0.3);border-radius:12px;background:rgba(23,34,71,0.96);backdrop-filter:blur(8px);color:#ffffff;font-size:12px;box-shadow:0 12px 32px rgba(0,0,0,0.65),0 0 16px rgba(245,158,11,0.2);pointer-events:none;animation:fadeInUp 0.2s ease-out}
.tip b{display:block;margin-bottom:4px;color:#fbbf24}
@media(max-width:768px){
 .bar{flex-wrap:wrap}.bar strong{flex:1 0 100%}.bar input{flex:1;width:auto}
 .root{justify-content:flex-start;padding:18px 0 16px}.root button{margin-left:26px}
 .areas{padding:0 14px 30px}
 .area{display:block;min-height:0;margin-bottom:24px}
 .area-inner,.area[data-side="left"] .area-inner{flex-direction:column;align-items:flex-start;gap:12px;padding:6px 0 16px}
 .area-title{width:min(100%,320px);margin-left:26px}
 .skill-group,.area[data-side="left"] .skill-group{width:calc(100% - 38px);margin-left:38px;justify-content:flex-start}
 .skill{min-height:42px;font-size:13px}
 .area[data-side="left"] .area-title .check,.area[data-side="left"] .skill .check{right:-9px;left:auto}
}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition-duration:.01ms!important}}
</style></head><body>
<div class="bar"><strong id="title">Career roadmap</strong><input id="search" type="search" placeholder="Find a skill…" aria-label="Search skills"><button id="reset" type="button">Fit full roadmap</button></div>
<div class="meter-label"><span style="color:#4e8d31">●</span> Already know &nbsp; <span style="color:#8b5cf6">●</span> To learn</div>
<main class="view" id="view"><div class="world" id="world"><svg class="svg" id="svg"></svg><div class="root" id="root"></div><div class="areas" id="areas"></div></div></main><div class="tip" id="tip"></div>
<script>
const DATA=JSON.parse(atob("__ROADMAP_DATA__"));
const viewEl=document.getElementById("view"),world=document.getElementById("world"),svg=document.getElementById("svg"),tip=document.getElementById("tip");
let transform={x:0,y:0,scale:1};
function buildLayout(data){
 if(!data||!Array.isArray(data.nodes))throw new Error("Roadmap must have nodes.");
 const map=new Map(data.nodes.map(n=>[n.id,n]));
 if(map.size!==data.nodes.length||data.nodes.some(n=>!n.id||!n.label||!["known","to_learn","none"].includes(n.status)))throw new Error("Invalid roadmap node data.");
 const roots=data.nodes.filter(n=>!n.parentId);if(roots.length!==1)throw new Error("Roadmap must have one root.");
 const root=roots[0],areas=data.nodes.filter(n=>n.parentId===root.id).sort((a,b)=>a.sequence-b.sequence);
 if(!areas.length||areas.some(area=>area.type!=="branch"))throw new Error("Every roadmap section must belong to the root.");
 const visited=new Set([root.id]),result=areas.map(area=>{
  if(visited.has(area.id))throw new Error("Duplicate roadmap section.");
  visited.add(area.id);
  const children=data.nodes.filter(n=>n.parentId===area.id).sort((a,b)=>a.sequence-b.sequence);
  if(!children.length||children.some(n=>n.type!=="skill"))throw new Error("Every section needs skill nodes.");
  children.forEach(n=>{if(visited.has(n.id))throw new Error("Roadmap contains a cycle.");visited.add(n.id);});
  return{...area,children};
 });
 if(visited.size!==map.size)throw new Error("Every skill must belong to one roadmap section.");
 return{root,areas:result,skills:result.flatMap(area=>area.children)};
}
function makeNode(node,kind){
 const button=document.createElement("button");button.type="button";button.className=kind;button.dataset.id=node.id;button.dataset.label=node.label.toLowerCase();button._data=node;
 button.setAttribute("aria-label",node.label+(node.url?", open learning resource in new tab":", show description"));
 if(kind==="root")button.textContent=node.label;else{
  const label=document.createElement("span");label.textContent=node.label;button.append(label);
  if(kind==="skill"){
   const isKnown=node.status==="known";const check=document.createElement("span");check.className="check"+(isKnown?" known":"");check.textContent=isKnown?"✓":"•";check.setAttribute("aria-hidden","true");button.append(check);
   button.setAttribute("aria-label",node.label+(isKnown?", already known":", to learn")+(node.url?", open learning resource in new tab":", show description"));
  }
 }
 return button;
}
function renderRoadmap(layout){
 document.getElementById("title").textContent=layout.root.label+" learning path";
 document.getElementById("root").replaceChildren(makeNode(layout.root,"root"));
 const container=document.getElementById("areas");container.replaceChildren();
 layout.areas.forEach((area,index)=>{
  const side=index%2===0?"right":"left";
  const section=document.createElement("section");section.className="area";section.dataset.id=area.id;section.dataset.side=side;
  const inner=document.createElement("div");inner.className="area-inner";
  const title=makeNode(area,"area-title");
  const skillGroup=document.createElement("div");skillGroup.className="skill-group";
  area.children.forEach(skill=>skillGroup.append(makeNode(skill,"skill")));
  inner.append(title,skillGroup);
  section.append(inner);
  container.append(section);
 });
 attachInteractions();fitView();draw(layout);
}
function draw(layout){
 const scale=transform.scale||1,wr=world.getBoundingClientRect(),width=world.clientWidth,height=world.scrollHeight;
 svg.setAttribute("width",width);svg.setAttribute("height",height);svg.setAttribute("viewBox",`0 0 ${width} ${height}`);svg.replaceChildren();
 const pos=el=>{const r=el.getBoundingClientRect();return{left:(r.left-wr.left)/scale,right:(r.right-wr.left)/scale,top:(r.top-wr.top)/scale,bottom:(r.bottom-wr.top)/scale,cx:(r.left+r.right-2*wr.left)/(2*scale),cy:(r.top+r.bottom-2*wr.top)/(2*scale)}};
 const path=(d,cls)=>{const p=document.createElementNS("http://www.w3.org/2000/svg","path");p.setAttribute("d",d);p.setAttribute("class",cls);svg.append(p)};
 const root=pos(document.querySelector("#root button")),sections=[...document.querySelectorAll(".area")];
 if(!sections.length||!root)return;
 const spineX=root.cx;
 const titles=sections.map(s=>pos(s.querySelector(".area-title")));
 const lastTitleCy=titles[titles.length-1].cy;
 path(`M ${spineX} ${root.bottom} L ${spineX} ${lastTitleCy}`,"solid");
 sections.forEach((section,index)=>{
  const title=titles[index];
  const side=section.dataset.side;
  const mobile=innerWidth<=820;
  if(mobile){
   path(`M ${spineX} ${title.cy} L ${title.left} ${title.cy}`,"solid");
   section.querySelectorAll(".skill").forEach(skillEl=>{
    const skill=pos(skillEl);
    const startY=title.bottom,endY=skill.top,mid=(startY+endY)/2;
    path(`M ${title.cx} ${startY} C ${title.cx} ${mid}, ${skill.cx} ${mid}, ${skill.cx} ${endY}`,"dotted");
   });
  }else{
   const isRight=side==="right";
   const branchAttachX=isRight?title.left:title.right;
   path(`M ${spineX} ${title.cy} L ${branchAttachX} ${title.cy}`,"solid");
   const titleSkillEdgeX=isRight?title.right:title.left;
   section.querySelectorAll(".skill").forEach(skillEl=>{
    const skill=pos(skillEl);
    const skillAttachX=isRight?skill.left:skill.right;
    const bend=Math.max(20,Math.abs(skillAttachX-titleSkillEdgeX)*.35);
    path(`M ${titleSkillEdgeX} ${title.cy} C ${titleSkillEdgeX+(isRight?bend:-bend)} ${title.cy}, ${skillAttachX-(isRight?bend:-bend)} ${skill.cy}, ${skillAttachX} ${skill.cy}`,"dotted");
   });
  }
 });
}
function attachInteractions(){
 document.querySelectorAll(".skill,.area-title,#root button").forEach(button=>{
  if(button._hasHandler)return;button._hasHandler=true;
  button.addEventListener("click",e=>{
   e.stopPropagation();const node=button._data;if(node.url){window.open(node.url,"_blank","noopener,noreferrer");return;}
   tip.replaceChildren();const title=document.createElement("b");title.textContent=node.label;const text=document.createElement("span");text.textContent=node.description||"No description available.";tip.append(title,text);
   const rect=button.getBoundingClientRect();tip.style.left=Math.max(10,Math.min(rect.left,innerWidth-290))+"px";tip.style.top=Math.min(rect.bottom+8,innerHeight-100)+"px";tip.style.display="block";
  });
 });
 const searchInput=document.getElementById("search");
 if(!searchInput._hasHandler){
  searchInput._hasHandler=true;
  searchInput.addEventListener("input",e=>{
   const q=e.target.value.trim().toLowerCase();
   document.querySelectorAll(".skill").forEach(node=>{
    const match=q&&node.dataset.label.includes(q);
    node.classList.toggle("match",Boolean(match));
    node.classList.toggle("dim",Boolean(q)&&!match);
   });
  });
 }
}
function fitView(){
 transform={x:0,y:0,scale:1};
 const vw=viewEl.clientWidth,vh=viewEl.clientHeight;
 const areasEl=document.getElementById("areas");
 const contentWidth=Math.max(areasEl ? areasEl.offsetWidth : 700, 680);
 const contentHeight=Math.max(world.scrollHeight, 380);
 if(vw>0 && vh>0){
  const scaleX=(vw-20)/contentWidth;
  const scaleY=(vh-20)/contentHeight;
  transform.scale=Math.max(.5,Math.min(1.0,Math.min(scaleX,scaleY)));
 }
 apply();
}
function apply(){
 world.style.transform=`translate(${transform.x}px,${transform.y}px) scale(${transform.scale})`;
 requestAnimationFrame(()=>draw(layout));
}
const layout=buildLayout(DATA);renderRoadmap(layout);
let drag=null;
viewEl.addEventListener("pointerdown",e=>{if(e.target.closest("button"))return;drag={x:e.clientX,y:e.clientY,ox:transform.x,oy:transform.y,id:e.pointerId};viewEl.setPointerCapture(e.pointerId);viewEl.classList.add("drag");});
viewEl.addEventListener("pointermove",e=>{if(!drag)return;transform.x=drag.ox+e.clientX-drag.x;transform.y=drag.oy+e.clientY-drag.y;apply();});
function end(){drag=null;viewEl.classList.remove("drag")}viewEl.addEventListener("pointerup",end);viewEl.addEventListener("pointercancel",end);
viewEl.addEventListener("wheel",e=>{e.preventDefault();const r=viewEl.getBoundingClientRect(),px=e.clientX-r.left,py=e.clientY-r.top,base=viewEl.clientWidth/2,next=Math.max(.45,Math.min(1.8,transform.scale*(e.deltaY<0?1.08:.92))),ratio=next/transform.scale;transform.x=px-base-(px-base-transform.x)*ratio;transform.y=py-(py-transform.y)*ratio;transform.scale=next;apply();},{passive:false});
document.getElementById("reset").addEventListener("click",()=>{tip.style.display="none";fitView();});
viewEl.addEventListener("click",e=>{if(!e.target.closest("button"))tip.style.display="none";});
window.addEventListener("resize",()=>requestAnimationFrame(fitView));
</script></body></html>"""
