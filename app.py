from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pandas as pd
import sqlite3
import pickle
import re
import os
from authlib.integrations.flask_client import OAuth
import secrets
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import webbrowser
import threading
from difflib import SequenceMatcher



skill_synonyms = {
    "ml": "machine learning",
    "ai": "machine learning",
    "js": "javascript",
    "html5": "html",
    "css3": "css",
    "accounts": "accounting",
    "bio": "biology",
    "dsa": "data structures",
    "comm": "communication",
    "stats": "statistics",
    "ui": "ui design",
    "ux": "ux design"
}

def normalize_skill(skill):
    skill = skill.strip().lower()
    
def normalize_skills(skill_list):
    normalized = []
    for skill in skill_list:
        skill = skill.strip().lower()
        if skill in skill_synonyms:
            skill = skill_synonyms[skill]
        normalized.append(skill)
    return normalized



app = Flask(__name__)



def is_similar(skill1, skill2):
    skill1 = skill1.lower()
    skill2 = skill2.lower()
    return SequenceMatcher(None, skill1, skill2).ratio() > 0.6
def get_missing_skills(user_skills, required_skills):
    missing = []
    
    for req in required_skills:
        found = False
        for user in user_skills:
            if is_similar(req, user):
                found = True
                break
        
        if not found:
            missing.append(req)
    
    return missing


app.secret_key = "smartcareer_dev_key"


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# ================= DATABASE =================
def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        password TEXT
    )
    """)

        # ✅ add reset_token column safely if not exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if "reset_token" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")

    if "is_admin" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        career TEXT
    )
    """)
    #cursor.execute("""
   # ALTER TABLE users ADD COLUMN reset_token TEXT
    #""")

    conn.commit()
    conn.close()

init_db()

# ================= LOAD TRAINED MODEL =================
model = pickle.load(open("models/career_model.pkl","rb"))
le_stream = pickle.load(open("models/le_stream.pkl","rb"))
le_interest = pickle.load(open("models/le_interest.pkl","rb"))
le_skill = pickle.load(open("models/le_skill.pkl","rb"))
le_career = pickle.load(open("models/le_career.pkl","rb"))
accuracy = 95.0

# ================= CAREER DETAILS =================
career_details = {
    "Machine Learning Engineer": {
        "skills": ["Python","ML","Statistics","Data Structures"],
        "certifications": ["Google ML","Coursera ML"],
        "tools": ["TensorFlow","Scikit-learn"],
        "roadmap": ["Learn Python","Learn ML","Build Projects","Apply Jobs"],
        "resume_tips": "Show ML projects and GitHub profile."
    },
    "Data Scientist": {
        "skills": ["Python","SQL","Data Analysis"],
        "certifications": ["IBM Data Science"],
        "tools": ["Pandas","Power BI"],
        "roadmap": ["Learn Python","Learn Visualization","Build Projects"],
        "resume_tips": "Add dashboards and real datasets."
    }
}


career_details.update({

# ================= TECH =================
"Software Developer": {
    "skills": ["Python","Java","Data Structures","Algorithms"],
    "certifications": ["Google IT Automation","Coursera Programming"],
    "tools": ["VS Code","Git","Docker"],
    "roadmap": ["Learn Programming","DSA","Build Projects","Apply Jobs"],
    "resume_tips": "Show projects and GitHub."
},

"Web Developer": {
    "skills": ["HTML","CSS","JavaScript","React"],
    "certifications": ["Meta Frontend Developer"],
    "tools": ["VS Code","Chrome DevTools"],
    "roadmap": ["Learn HTML/CSS","JS","Framework","Build Projects"],
    "resume_tips": "Show live websites."
},

"Cyber Security Analyst": {
    "skills": ["Networking","Security","Ethical Hacking"],
    "certifications": ["CEH","CompTIA Security+"],
    "tools": ["Wireshark","Kali Linux"],
    "roadmap": ["Learn Networking","Security Basics","Practice Labs"],
    "resume_tips": "Add security projects."
},

"Cloud Engineer": {
    "skills": ["Cloud","Linux","Networking"],
    "certifications": ["AWS Certified","Azure Fundamentals"],
    "tools": ["AWS","Docker","Kubernetes"],
    "roadmap": ["Learn Cloud","Deploy Apps","Get Certified"],
    "resume_tips": "Mention cloud deployments."
},

"DevOps Engineer": {
    "skills": ["CI/CD","Linux","Scripting"],
    "certifications": ["Docker Certified"],
    "tools": ["Jenkins","Docker","Kubernetes"],
    "roadmap": ["Learn Linux","Automation","CI/CD"],
    "resume_tips": "Show automation pipelines."
},

"UI/UX Designer": {
    "skills": ["Design","Creativity","User Research"],
    "certifications": ["Google UX Design"],
    "tools": ["Figma","Adobe XD"],
    "roadmap": ["Learn Design","Create Portfolio","User Testing"],
    "resume_tips": "Show design portfolio."
},

# ================= DATA =================
"Business Analyst": {
    "skills": ["Excel","SQL","Analysis"],
    "certifications": ["CBAP"],
    "tools": ["Excel","Power BI"],
    "roadmap": ["Learn Analysis","SQL","Dashboards"],
    "resume_tips": "Show data insights."
},

"Data Analyst": {
    "skills": ["Python","SQL","Data Visualization"],
    "certifications": ["Google Data Analytics"],
    "tools": ["Pandas","Tableau"],
    "roadmap": ["Learn Python","SQL","Visualization"],
    "resume_tips": "Add dashboards."
},

# ================= MEDICAL =================
"Doctor": {
    "skills": ["Medical Knowledge","Diagnosis","Communication"],
    "certifications": ["MBBS"],
    "tools": ["Medical Equipment"],
    "roadmap": ["NEET","MBBS","Internship","Practice"],
    "resume_tips": "Mention internships."
},

"Nurse": {
    "skills": ["Patient Care","Medical Support"],
    "certifications": ["BSc Nursing"],
    "tools": ["Hospital Tools"],
    "roadmap": ["Nursing Course","Hospital Training"],
    "resume_tips": "Highlight patient care."
},

"Pharmacist": {
    "skills": ["Medicine Knowledge","Chemistry"],
    "certifications": ["B.Pharm"],
    "tools": ["Pharmacy Systems"],
    "roadmap": ["Pharmacy Degree","License"],
    "resume_tips": "Show certifications."
},

# ================= COMMERCE =================
"Chartered Accountant": {
    "skills": ["Accounting","Finance","Taxation"],
    "certifications": ["CA"],
    "tools": ["Tally","Excel"],
    "roadmap": ["CA Foundation","Inter","Final"],
    "resume_tips": "Show finance knowledge."
},

"Investment Banker": {
    "skills": ["Finance","Analysis"],
    "certifications": ["CFA"],
    "tools": ["Excel","Bloomberg"],
    "roadmap": ["Finance Degree","Internship"],
    "resume_tips": "Show finance projects."
},

"Banker": {
    "skills": ["Finance","Communication"],
    "certifications": ["Bank Exams"],
    "tools": ["Banking Software"],
    "roadmap": ["Prepare Exams","Join Bank"],
    "resume_tips": "Show banking skills."
},

# ================= MANAGEMENT =================
"HR Manager": {
    "skills": ["Communication","Management"],
    "certifications": ["MBA HR"],
    "tools": ["HR Software"],
    "roadmap": ["MBA","Internship"],
    "resume_tips": "Show leadership."
},

"Marketing Manager": {
    "skills": ["Marketing","Strategy"],
    "certifications": ["MBA Marketing"],
    "tools": ["Google Ads"],
    "roadmap": ["Learn Marketing","Campaigns"],
    "resume_tips": "Show campaigns."
},

"Digital Marketer": {
    "skills": ["SEO","Social Media"],
    "certifications": ["Google Digital Marketing"],
    "tools": ["Google Analytics"],
    "roadmap": ["Learn SEO","Run Ads"],
    "resume_tips": "Show results."
},

# ================= CREATIVE =================
"Graphic Designer": {
    "skills": ["Design","Creativity"],
    "certifications": ["Adobe"],
    "tools": ["Photoshop","Illustrator"],
    "roadmap": ["Learn Tools","Build Portfolio"],
    "resume_tips": "Show designs."
},

"Content Writer": {
    "skills": ["Writing","SEO"],
    "certifications": ["Content Marketing"],
    "tools": ["Grammarly"],
    "roadmap": ["Write Blogs","Freelance"],
    "resume_tips": "Show articles."
},

"Video Editor": {
    "skills": ["Editing","Creativity"],
    "certifications": ["Adobe Premiere"],
    "tools": ["Premiere Pro"],
    "roadmap": ["Learn Editing","Create Videos"],
    "resume_tips": "Show videos."
},

# ================= EDUCATION =================
"Teacher": {
    "skills": ["Teaching","Communication"],
    "certifications": ["B.Ed"],
    "tools": ["Smart Boards"],
    "roadmap": ["Degree","Teaching Practice"],
    "resume_tips": "Show teaching experience."
},

"Professor": {
    "skills": ["Research","Teaching"],
    "certifications": ["PhD"],
    "tools": ["Academic Tools"],
    "roadmap": ["Masters","PhD"],
    "resume_tips": "Show research."
},

# ================= LAW =================
"Lawyer": {
    "skills": ["Law Knowledge","Argument"],
    "certifications": ["LLB"],
    "tools": ["Legal Tools"],
    "roadmap": ["Law Degree","Practice"],
    "resume_tips": "Show cases."
},

"Judge": {
    "skills": ["Law","Decision Making"],
    "certifications": ["Judicial Exams"],
    "tools": ["Court Systems"],
    "roadmap": ["Law Degree","Exam"],
    "resume_tips": "Show law knowledge."
},

# ================= ENGINEERING =================
"Civil Engineer": {
    "skills": ["Construction","Design"],
    "certifications": ["B.Tech Civil"],
    "tools": ["AutoCAD"],
    "roadmap": ["Engineering Degree","Projects"],
    "resume_tips": "Show site work."
},

"Mechanical Engineer": {
    "skills": ["Machines","Design"],
    "certifications": ["B.Tech Mechanical"],
    "tools": ["SolidWorks"],
    "roadmap": ["Engineering Degree","Projects"],
    "resume_tips": "Show projects."
},

"Electrical Engineer": {
    "skills": ["Circuits","Electrical Systems"],
    "certifications": ["B.Tech Electrical"],
    "tools": ["MATLAB"],
    "roadmap": ["Learn Circuits","Projects"],
    "resume_tips": "Show technical work."
},

# ================= GOVERNMENT =================
"IAS Officer": {
    "skills": ["General Knowledge","Leadership"],
    "certifications": ["UPSC"],
    "tools": ["Study Material"],
    "roadmap": ["Prepare UPSC","Clear Exam"],
    "resume_tips": "Show achievements."
},

"Police Officer": {
    "skills": ["Fitness","Discipline"],
    "certifications": ["Police Exams"],
    "tools": ["Police Systems"],
    "roadmap": ["Prepare Exams","Training"],
    "resume_tips": "Show discipline."
},

# ================= OTHER =================
"Entrepreneur": {
    "skills": ["Business","Leadership"],
    "certifications": ["Startup Courses"],
    "tools": ["Business Tools"],
    "roadmap": ["Idea","Startup","Scale"],
    "resume_tips": "Show business experience."
},

"Freelancer": {
    "skills": ["Skill Based","Communication"],
    "certifications": ["Online Courses"],
    "tools": ["Upwork","Fiverr"],
    "roadmap": ["Learn Skill","Get Clients"],
    "resume_tips": "Show client work."
},

"Event Manager": {
    "skills": ["Management","Planning"],
    "certifications": ["Event Management"],
    "tools": ["Planning Tools"],
    "roadmap": ["Learn Event Planning"],
    "resume_tips": "Show events."
},

"Hotel Manager": {
    "skills": ["Hospitality","Management"],
    "certifications": ["Hotel Management"],
    "tools": ["Hotel Systems"],
    "roadmap": ["Course","Internship"],
    "resume_tips": "Show hospitality skills."
},

"Pilot": {
    "skills": ["Flying","Focus"],
    "certifications": ["Commercial Pilot License"],
    "tools": ["Aircraft Systems"],
    "roadmap": ["Training","License"],
    "resume_tips": "Show flight hours."
}

})

# ================= STREAM SKILLS (STEP E) =================
stream_skills = {
    "arts": ["writing", "creativity", "communication"],
    "commerce": ["accounting", "excel", "business"],
    "pcm": ["math", "logic", "problem solving"],
    "pcb": ["biology", "research", "analysis"]
}

course_data = {

"python": [
    {"name": "Python Full Course", "platform": "YouTube",
     "link": "https://www.youtube.com/watch?v=_uQrJ0TkZlc"},

    {"name": "Python for Data Science", "platform": "IBM",
     "link": "https://cognitiveclass.ai/courses/python-for-data-science"},

    {"name": "Infosys Python Course", "platform": "Infosys",
     "link": "https://infyspringboard.onwingspan.com/"}
],

"sql": [
    {"name": "SQL Full Course", "platform": "YouTube",
     "link": "https://www.youtube.com/watch?v=HXV3zeQKqGY"},

    {"name": "NPTEL SQL Course", "platform": "NPTEL",
     "link": "https://nptel.ac.in/courses"},

    {"name": "Infosys SQL Course", "platform": "Infosys",
     "link": "https://infyspringboard.onwingspan.com/"}
],

"machine learning": [
    {"name": "ML Full Course", "platform": "YouTube",
     "link": "https://www.youtube.com/watch?v=GwIo3gDZCVQ"},

    {"name": "Google ML Crash Course", "platform": "Google",
     "link": "https://developers.google.com/machine-learning/crash-course"}
],

"web development": [
    {"name": "Web Dev Full Course", "platform": "YouTube",
     "link": "https://www.youtube.com/watch?v=Q33KBiDriJY"},

    
]
}

all_courses = [

         # ================= INFOSYS =================
    {"name": "Infosys Python Course",
     "platform": "Infosys",
     "level": "Beginner",
     "link": "https://infyspringboard.onwingspan.com/web/en/app/toc/lex_auth_01269593357650329655"},

    {"name": "Infosys Data Science",
     "platform": "Infosys",
     "level": "Intermediate",
     "link": "https://infyspringboard.onwingspan.com/"},

    # ================= IBM =================
    {"name": "IBM Data Science Basics",
     "platform": "IBM",
     "level": "Beginner",
     "link": "https://cognitiveclass.ai/courses/data-science-101/"},

    {"name": "IBM Python Course",
     "platform": "IBM",
     "level": "Beginner",
     "link": "https://cognitiveclass.ai/courses/python-for-data-science"},

    # ================= NPTEL =================
    {"name": "NPTEL Computer Science Courses",
     "platform": "NPTEL",
     "level": "Intermediate",
     "link": "https://nptel.ac.in/courses"},

    {"name": "NPTEL Programming in Python",
     "platform": "NPTEL",
    "level": "Beginner",
    "link": "https://nptel.ac.in/courses/106106145"},

    {"name": "NPTEL Data Structures & Algorithms",
    "platform": "NPTEL",
     "level": "Intermediate",
     "link": "https://nptel.ac.in/courses/106102064"},

    {"name": "NPTEL Engineering Courses",
    "platform": "NPTEL",
    "level": "Intermediate",
    "link": "https://nptel.ac.in/course.html"},

    {"name": "NPTEL Cloud Computing",
    "platform": "NPTEL",
    "level": "Advanced",
    "link": "https://nptel.ac.in/courses/106105167"},

   {"name": "NPTEL Machine Learning",
   "platform": "NPTEL",
   "level": "Intermediate",
    "link": "https://nptel.ac.in/courses/106106139"},

    # ================= SWAYAM =================
    {"name": "SWAYAM Computer Courses",
     "platform": "SWAYAM",
     "level": "Beginner",
     "link": "https://swayam.gov.in/explorer?category=Computer%20Science"},

    {"name": "SWAYAM Management Courses",
     "platform": "SWAYAM",
     "level": "Intermediate",
     "link": "https://swayam.gov.in/explorer?category=Management"},

    {"name": "SWAYAM Humanities Courses",
     "platform": "SWAYAM",
     "level": "Beginner",
     "link": "https://swayam.gov.in/explorer?category=Humanities"},

    # ================= FREE EDUCATION =================
    {"name": "Khan Academy Courses",
     "platform": "Khan Academy",
     "level": "Beginner",
     "link": "https://www.khanacademy.org/"},

    {"name": "freeCodeCamp Full Courses",
     "platform": "freeCodeCamp",
     "level": "Beginner",
     "link": "https://www.freecodecamp.org/learn/"},

    {"name": "MIT OpenCourseWare",
     "platform": "MIT",
     "level": "Advanced",
     "link": "https://ocw.mit.edu/"},

    {"name": "Harvard Free Courses",
     "platform": "Harvard",
     "level": "Intermediate",
     "link": "https://pll.harvard.edu/catalog/free"},

    {"name": "Google Digital Garage",
     "platform": "Google",
     "level": "Beginner",
     "link": "https://learndigital.withgoogle.com/digitalgarage"},


    # ================= PROGRAMMING =================
    {"name": "Python Full Course",
     "platform": "YouTube",
     "level": "Beginner",
     "link": "https://www.youtube.com/watch?v=_uQrJ0TkZlc"},

    {"name": "Python Advanced Projects",
     "platform": "YouTube",
     "level": "Intermediate",
     "link": "https://www.youtube.com/results?search_query=python+projects+full+course"},

    {"name": "Java Full Course",
     "platform": "YouTube",
     "level": "Beginner",
     "link": "https://www.youtube.com/results?search_query=java+full+course"},

    {"name": "C Programming Full Course",
     "platform": "YouTube",
     "level": "Beginner",
     "link": "https://www.youtube.com/results?search_query=c+programming+full+course"},

    {"name": "C++ Full Course",
     "platform": "YouTube",
     "level": "Intermediate",
      "link": "https://www.youtube.com/results?search_query=c%2B%2B+full+course"},

    # ================= WEB DEVELOPMENT =================
    {"name": "HTML CSS Full Course",
     "platform": "YouTube",
     "level": "Beginner",
     "link": "https://www.youtube.com/results?search_query=html+css+full+course"},

    {"name": "JavaScript Full Course",
     "platform": "YouTube",
     "level": "Intermediate",
     "link": "https://www.youtube.com/results?search_query=javascript+full+course"},

    {"name": "React JS Full Course",
     "platform": "YouTube",
     "level": "Intermediate",
     "link": "https://www.youtube.com/results?search_query=react+js+full+course"},

    {"name": "Full Stack Development",
     "platform": "YouTube",
     "level": "Advanced",
     "link": "https://www.youtube.com/results?search_query=full+stack+development+course"},

      # ================= DATA SCIENCE =================
    {"name": "Data Science Full Course",
     "platform": "YouTube",
     "level": "Intermediate",
     "link": "https://www.youtube.com/results?search_query=data+science+full+course"},

    {"name": "Machine Learning Complete Course",
     "platform": "YouTube",
     "level": "Intermediate",
     "link": "https://www.youtube.com/results?search_query=machine+learning+full+course"},

    {"name": "Deep Learning Course",
     "platform": "YouTube",
     "level": "Advanced",
     "link": "https://www.youtube.com/results?search_query=deep+learning+full+course"},

    {"name": "SQL Complete Course",
     "platform": "YouTube",
     "level": "Beginner",
     "link": "https://www.youtube.com/results?search_query=sql+full+course"},

    {"name": "Power BI Full Course",
     "platform": "YouTube",
     "level": "Intermediate",
     "link": "https://www.youtube.com/results?search_query=power+bi+full+course"},

     # ================= CYBER SECURITY =================
    {"name": "Cyber Security Full Course",
     "platform": "YouTube",
     "level": "Intermediate",
     "link": "https://www.youtube.com/results?search_query=cyber+security+full+course"},

    {"name": "Ethical Hacking Course",
     "platform": "YouTube",
     "level": "Advanced",
     "link": "https://www.youtube.com/results?search_query=ethical+hacking+full+course"},

    {"name": "Networking Basics",
     "platform": "YouTube",
     "level": "Beginner",
     "link": "https://www.youtube.com/results?search_query=computer+networking+full+course"},

    # ================= CLOUD =================
    {"name": "AWS Cloud Basics",
     "platform": "YouTube",
     "level": "Beginner",
     "link": "https://www.youtube.com/results?search_query=aws+cloud+course"},

    {"name": "Docker Full Course",
     "platform": "YouTube",
     "level": "Intermediate",
     "link": "https://www.youtube.com/results?search_query=docker+full+course"},

    {"name": "Kubernetes Full Course",
     "platform": "YouTube",
     "level": "Advanced",
     "link": "https://www.youtube.com/results?search_query=kubernetes+full+course"},
    
    # ================= COMMERCE =================
    {"name": "Accounting Full Course",
     "platform": "YouTube",
     "level": "Beginner",
     "link": "https://www.youtube.com/results?search_query=accounting+full+course"},

    {"name": "Stock Market Basics",
     "platform": "YouTube",
     "level": "Beginner",
     "link": "https://www.youtube.com/results?search_query=stock+market+course"},

    {"name": "Finance Management Course",
     "platform": "YouTube",
     "level": "Intermediate",
     "link": "https://www.youtube.com/results?search_query=finance+management+course"},

    # ================= MEDICAL =================
    {"name": "Human Anatomy Full Course",
     "platform": "YouTube",
     "level": "Beginner",
     "link": "https://www.youtube.com/results?search_query=human+anatomy+course"},

    {"name": "Biology Full Course",
     "platform": "YouTube",
     "level": "Beginner",
     "link": "https://www.youtube.com/results?search_query=biology+full+course"},

    {"name": "Medical Entrance Preparation",
     "platform": "YouTube",
     "level": "Intermediate",
     "link": "https://www.youtube.com/results?search_query=neet+preparation+full+course"},

    # ================= ARTS =================
    {"name": "Graphic Design Course",
     "platform": "YouTube",
     "level": "Beginner",
     "link": "https://www.youtube.com/results?search_query=graphic+design+full+course"},

    {"name": "Content Writing Course",
     "platform": "YouTube",
     "level": "Beginner",
     "link": "https://www.youtube.com/results?search_query=content+writing+course"},

    {"name": "Video Editing Course",
     "platform": "YouTube",
     "level": "Intermediate",
     "link": "https://www.youtube.com/results?search_query=video+editing+full+course"},

    # ================= GOVERNMENT / EXAMS =================
    {"name": "UPSC Preparation",
     "platform": "YouTube",
     "level": "Intermediate",
     "link": "https://www.youtube.com/results?search_query=upsc+preparation+course"},

    {"name": "SSC Exam Preparation",
     "platform": "YouTube",
     "level": "Beginner",
     "link": "https://www.youtube.com/results?search_query=ssc+exam+preparation+course"},

    {"name": "Banking Exam Preparation",
     "platform": "YouTube",
     "level": "Intermediate",
     "link": "https://www.youtube.com/results?search_query=bank+exam+preparation+course"},

      
]

stream_courses = {

    "pcm": [
        {"name": "Engineering Courses (All Platforms)",
         "link": "https://www.google.com/search?q=engineering+courses+online"},

        {"name": "Programming Courses",
         "link": "https://www.google.com/search?q=python+java+courses+online"}
    ],

    "pcb": [
        {"name": "Medical Courses",
         "link": "https://www.google.com/search?q=medical+courses+online"},

        {"name": "Biology Courses",
         "link": "https://www.google.com/search?q=biology+courses+online"}
    ],

    "commerce": [
        {"name": "Accounting Courses",
         "link": "https://www.google.com/search?q=accounting+courses+online"},

        {"name": "Finance Courses",
         "link": "https://www.google.com/search?q=finance+courses+online"}
    ],

    "arts": [
        {"name": "Design Courses",
         "link": "https://www.google.com/search?q=design+courses+online"},

         {"name": "Writing Courses",
         "link": "https://www.google.com/search?q=content+writing+courses"}
    ]
}

extra_stream_courses = {

    "pcm": [
        {"name": "Engineering Courses (All Platforms)",
         "platform": "Google",
         "level": "Beginner",
         "link": "https://www.google.com/search?q=engineering+courses+online"},

        {"name": "Programming Courses",
         "platform": "Google",
         "level": "Beginner",
         "link": "https://www.google.com/search?q=python+java+courses+online"}
    ],

    "pcb": [
        {"name": "Medical Courses",
         "platform": "Google",
         "level": "Beginner",
         "link": "https://www.google.com/search?q=medical+courses+online"},

        {"name": "Biology Courses",
         "platform": "Google",
         "level": "Intermediate",
         "link": "https://www.google.com/search?q=biology+courses+online"}
    ],
    "commerce": [
        {"name": "Accounting Courses",
         "platform": "Google",
         "level": "Beginner",
         "link": "https://www.google.com/search?q=accounting+courses+online"},

        {"name": "Finance Courses",
         "platform": "Google",
         "level": "Intermediate",
         "link": "https://www.google.com/search?q=finance+courses+online"}
    ],

    "arts": [
        {"name": "Design Courses",
         "platform": "Google",
         "level": "Beginner",
         "link": "https://www.google.com/search?q=design+courses+online"},

        {"name": "Writing Courses",
         "platform": "Google",
         "level": "Beginner",
         "link": "https://www.google.com/search?q=content+writing+courses"}
    ]
}




# ================= STEP 2 — SMART CAREER DETECTION =================

def detect_best_career(user_skills):
    best_match = None
    max_score = 0

    for career, details in career_details.items():
        required = [s.lower() for s in details["skills"]]

        score = 0
        for u in user_skills:
          for r in required:
             if is_similar(u, r):
                score += 1

        if score > max_score:
            max_score = score
            best_match = career

    return best_match


#======================STEP 3 -Hybrid fallback CAREEE INFO=================
stream_skill_map = {
    "pcm": ["maths", "physics", "problem solving"],
    "pcb": ["biology", "medical knowledge"],
    "pcmb": ["biology", "maths", "analysis"],
    "commerce": ["accounting", "finance", "business"],
    "arts": ["creativity", "communication", "writing"]
}

def detect_stream(user_skills):
    skills = [s.lower() for s in user_skills]

    pcm_keywords = [
        "math", "maths", "physics", "coding", "python", "java",
        "programming", "engineering", "technology", "computer"
    ]

    pcb_keywords = [
        "biology", "medical", "doctor", "healthcare",
        "anatomy", "medicine", "nursing"
    ]

    commerce_keywords = [
        "finance", "accounting", "business", "economics",
        "marketing", "banking", "tax"
    ]

    arts_keywords = [
        "design", "writing", "communication", "psychology",
        "creativity", "media", "journalism"
    ]

    if any(skill in pcm_keywords for skill in skills):
        return "pcm"

    elif any(skill in pcb_keywords for skill in skills):
        return "pcb"

    elif any(skill in commerce_keywords for skill in skills):
        return "commerce"

    elif any(skill in arts_keywords for skill in skills):
        return "arts"

    return None

# ================= 🔥 HYBRID FALLBACK =================
def get_dynamic_career_info(career):
    return {
        "skills": ["Problem Solving", "Communication", "Domain Knowledge"],
        "certifications": ["Online Courses", "Internship"],
        "tools": ["Industry Tools"],
        "roadmap": [
            f"Learn basics of {career}",
            "Build projects",
            "Do internship",
            "Apply for jobs"
        ],
        "resume_tips": f"Highlight your {career} related skills and projects."
    }


# ================= AUTH ROUTES =================


# ================= VALIDATIONS =================

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_strong_password(password):
    if (len(password) >= 8 and
        re.search("[A-Z]", password) and
        re.search("[a-z]", password) and
        re.search("[0-9]", password) and
        re.search("[@#$%^&+=]", password)):
        return True
    return False

def normalize_email(email):
    return email.strip().lower()

def find_user_by_login(login_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE lower(username)=? OR lower(email)=?",
        (login_id.strip().lower(), login_id.strip().lower())
    )
    user = cursor.fetchone()
    conn.close()
    return user

def find_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE lower(email)=?", (normalize_email(email),))
    user = cursor.fetchone()
    conn.close()
    return user

def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            flash("Please login first.", "warning")
            return redirect(url_for("login"))

        if not session.get("is_admin", 0):
            flash("Access denied.", "danger")
            return redirect(url_for("dashboard"))

        return view_func(*args, **kwargs)
    return wrapper


# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():

    print("REGISTER ROUTE HIT", request.method, dict(session))

    if request.method == "GET":
        return render_template("register.html")

    # ✅ SAFE FORM
    username = request.form.get("username", "").strip()
    email = normalize_email(request.form.get("email", ""))
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    # ✅ VALIDATIONS
    if not username or len(username) < 3:
        flash("Username must be at least 3 characters long.", "danger")
        return redirect(url_for("register"))

    if not is_valid_email(email):
        flash("Invalid email format.", "danger")
        return redirect(url_for("register"))

    if not is_strong_password(password):
        flash("Password must be strong (8+ chars, uppercase, lowercase, number, special char).", "danger")
        return redirect(url_for("register"))

    if password != confirm_password:
        flash("Passwords do not match.", "danger")
        return redirect(url_for("register"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ CHECK USERNAME
    cursor.execute("SELECT * FROM users WHERE lower(username)=?", (username.lower(),))
    if cursor.fetchone():
        conn.close()
        flash("Username already exists.", "danger")
        return redirect(url_for("register"))

    # ✅ CHECK EMAIL
    cursor.execute("SELECT * FROM users WHERE lower(email)=?", (email,))
    if cursor.fetchone():
        conn.close()
        flash("Email already exists.", "danger")
        return redirect(url_for("register"))

    # ✅ SAVE USER
    hashed_password = generate_password_hash(password)

    cursor.execute(
        "INSERT INTO users(username, email, password) VALUES (?, ?, ?)",
        (username, email, hashed_password)
    )
    conn.commit()
    conn.close()

    session.clear()
    flash("Registration successful! Please login.", "success")
    return redirect(url_for("login"))



# ================= LOGIN  =================
@app.route("/login", methods=["GET", "POST"])
def login():
    import time

    print("LOGIN ROUTE HIT", request.method, dict(session))

     # ✅ clear old flash (important fix)
    
    if "attempts" not in session:
        session["attempts"] = 0

    if "last_login_id" not in session:
        session["last_login_id"] = ""

    if "lock_until" not in session:
        session["lock_until"] = 0

    if request.method == "GET":
      return render_template("login.html")

# 🔒 LOCK CHECK (BEST VERSION)
    if time.time() < session["lock_until"]:
      remaining_time = int(session["lock_until"] - time.time())
      minutes = remaining_time // 60
      seconds = remaining_time % 60

      flash(f"Account locked. Try again in {minutes}m {seconds}s", "danger")
      return render_template("login.html")
    
    import time

    

    # ✅ SAFE FORM
    login_id = request.form.get("login_id", "").strip()
    password = request.form.get("password", "")
    remember = request.form.get("remember")

    if not login_id or not password:
        flash("Please fill in all fields.", "danger")
        return redirect(url_for("login"))

    normalized_login = login_id.lower()

    if session["last_login_id"] != normalized_login:
        session["attempts"] = 0
        session["last_login_id"] = normalized_login

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
    "SELECT * FROM users WHERE LOWER(username)=? OR LOWER(email)=?",
    (normalized_login, normalized_login)
)

    user = cursor.fetchone()
    conn.close()

# 🔍 DEBUG yaha add hoga
    print("LOGIN:", normalized_login)
    print("USER FROM DB:", user)


    # ✅ SUCCESS LOGIN
    if user and check_password_hash(user["password"], password):
       
        session.pop("attempts", None)
        session.pop("lock_until", None)
        session.pop("last_login_id", None)
        session["user"] = user["username"]
        session["user_id"] = user["id"]
        session["email"] = user["email"]
        session["is_admin"] = user["is_admin"] if "is_admin" in user.keys() else 0

       

       
    # ✅ RESET LOGIN ATTEMPTS
        session["attempts"] = 0
        session["lock_until"] = 0

        
        if remember:
            session.permanent = True
        else:
             session.permanent = False

        flash(f"Welcome back, {user['username']}!", "success")
        return redirect(url_for("dashboard"))

    # ❌ FAILED LOGIN
    if not user:
       session["attempts"] = session.get("attempts", 0) + 1
    elif not check_password_hash(user["password"], password):
       session["attempts"] = session.get("attempts", 0) + 1

    if session["attempts"] >= 3:
        session["lock_until"] = time.time() + 300  # 5 min lock
        flash("Too many attempts. Account locked for 5 minutes.", "danger")
    else:
        remaining = 3 - session["attempts"]
        flash(f"Invalid username/email or password. {remaining} attempts left.", "danger")

    return redirect(url_for("login"))
# ================= GOOGLE LOGIN (DUMMY) =================
@app.route("/google_login")
def google_login():
    session.clear()

    source = request.args.get("next")  # login ya register

    user_name = "Google User"
    user_email = "googleuser@gmail.com"

    session["user"] = user_name
    session["user_id"] = "google_" + user_email.split("@")[0]
    session["email"] = user_email
    session["is_admin"] = 0
    session.permanent = True

    if source == "register":
        flash("Account created with Google 🎉", "success")
    else:
        flash("Logged in with Google 🚀", "success")

    return redirect(url_for("dashboard"))

# ================= FORGOT PASSWORD =================
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = normalize_email(request.form["email"])

        if not email:
            flash("Please enter your email.", "danger")
            return redirect(url_for("forgot_password"))

        user = find_user_by_email(email)

        if user:
            token = secrets.token_urlsafe(32)

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET reset_token=? WHERE email=?", (token, email))
            conn.commit()
            conn.close()

            reset_link = url_for("reset_password", token=token, _external=True)
            print("Reset Link:", reset_link)

           
            return redirect(reset_link)

        flash("Email not found.", "danger")
        return redirect(url_for("forgot_password"))

    return render_template("forgot_password.html")

#========RESET PASSWORD=================
@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE reset_token=?", (token,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_password = request.form["password"]
        confirm_password = request.form.get("confirm_password", "")

        if not is_strong_password(new_password):
            flash("Password must be strong.", "danger")
            return redirect(url_for("reset_password", token=token))

        if new_password != confirm_password:
            flash("Password and confirm password do not match.", "danger")
            return redirect(url_for("reset_password", token=token))

        hashed_password = generate_password_hash(new_password)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password=?, reset_token=NULL WHERE reset_token=?",
            (hashed_password, token)
        )
        conn.commit()
        conn.close()
        session["attempts"] = 0
        session["lock_until"] = 0
        flash("Password updated successfully! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html", token=token)

#=======LOGOUT=================
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))

# ================= MAIN ROUTES =================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=session.get("user"))


@app.route("/recommendation", methods=["GET", "POST"])
@login_required
def recommendation():

   

    if request.method == "POST":

        try:
            stream = request.form["stream"]
            interest = request.form["interest"]
            skill_level = request.form["skill_level"]

            math = int(request.form["math_score"])
            communication = int(request.form["communication"])
            technical = int(request.form["technical_skill_score"])
            creativity = int(request.form["creativity_score"])
            aptitude = int(request.form["aptitude"])

            if stream not in le_stream.classes_:
                return "Invalid Stream Selected"
            if interest not in le_interest.classes_:
                return "Invalid Interest Selected"
            if skill_level not in le_skill.classes_:
                return "Invalid Skill Level Selected"

            # ================= INPUT DATA =================
            input_data = pd.DataFrame([{
                "Stream": le_stream.transform([stream])[0],
                "Interest": le_interest.transform([interest])[0],
                "Math_Score": math,
                "Communication_Score": communication,
                "Technical_Skill_Score": technical,
                "Creativity_Score": creativity,
                "Aptitude_Score": aptitude,
                "Skill_Level": le_skill.transform([skill_level])[0]
            }])

            # ================= NEW FEATURES =================
            input_data["Tech_Strength"] = (technical + math) / 2
            input_data["Soft_Strength"] = (communication + creativity) / 2
            input_data["Overall_Score"] = (math + technical + communication + creativity + aptitude) / 5

            # ================= PREDICTION =================
            probs = model.predict_proba(input_data)[0]
            top_idx = probs.argsort()[-3:][::-1]

            result = []
            for idx in top_idx:
                career = le_career.inverse_transform([model.classes_[idx]])[0]
                confidence = round(probs[idx]*100, 2)
                result.append({"career": career, "confidence": confidence})

            # ================= SAVE HISTORY =================
            # ✅ CORRECT (history में save करो)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO history(username,career) VALUES(?,?)",
               (session["user"], result[0]["career"]))

            conn.commit()
            conn.close()
            # ================= EXPLANATION =================
            explanation = []
            if math >= 80: explanation.append("High Math Score")
            if technical >= 80: explanation.append("Strong Technical Skill")
            if communication >= 70: explanation.append("Good Communication Skill")
            if creativity >= 70: explanation.append("High Creativity")
            if aptitude >= 75: explanation.append("Strong Aptitude Ability")

            explanation.append(f"Interest in {interest}")

            # ================= HYBRID =================
            career_name = result[0]["career"]

            if career_name in career_details:
                career_info = career_details[career_name]
            else:
                career_info = get_dynamic_career_info(career_name)

            session["result_data"] = {
                "result": result,
                "accuracy": accuracy,
                "career_info": career_info,
                "explanation": explanation
            }

            return redirect(url_for("result"))

        except Exception as e:
            return f"ERROR: {str(e)}"

    return render_template("recommendation.html",
                           streams=le_stream.classes_,
                           interests=le_interest.classes_,
                           skill_levels=le_skill.classes_)


@app.route("/result")
@login_required
def result():
    data = session.get("result_data")

    if not data:
        flash("Please complete the quiz first.", "warning")
        return redirect(url_for("recommendation"))

    return render_template("result.html", **data)


@app.route("/history")
@login_required
def history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT career FROM history WHERE username=?", (session["user"],))
    rows = cursor.fetchall()
    conn.close()

    return render_template("history.html", rows=rows)


# ================= EXTRA ROUTES =================
from flask import jsonify

@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()
    msg = data.get("message").lower()

    try:
        # 🎯 STREAM BASED ANSWERS
        if any(x in msg for x in ["pcm", "engineering", "maths"]):
            reply = """💻 PCM Career Options:
• Software Engineer
• Data Scientist
• Mechanical Engineer
• Civil Engineer
• Game Developer

📚 Courses:
• B.Tech / BE
• BCA
• BSc IT

🧠 Skills:
Coding, Problem Solving, Maths"""

        elif any(x in msg for x in ["pcb", "medical", "biology"]):
            reply = """🏥 PCB Career Options:
• Doctor (MBBS)
• Dentist (BDS)
• Pharmacist
• Biotech Engineer

📚 Courses:
• MBBS
• BDS
• B.Pharm
• BSc Biology

🧠 Skills:
Biology, Patience, Observation"""

        elif "pcmb" in msg:
            reply = """🔥 PCMB (Best Combo)

👉 You can go BOTH:
• Engineering 💻
• Medical 🏥

📚 Courses:
• MBBS / BTech / BSc

💡 You have maximum flexibility!"""

        elif any(x in msg for x in ["commerce", "accounts"]):
            reply = """💰 Commerce Career Options:
• CA
• CS
• BBA / MBA
• Banking
• Finance Analyst

📚 Courses:
• B.Com
• BBA
• CA / CS

🧠 Skills:
Accounting, Finance, Communication"""

        elif any(x in msg for x in ["arts", "humanities"]):
            reply = """🎨 Arts Career Options:
• Lawyer ⚖️
• Journalist 📰
• Designer 🎨
• Psychologist 🧠

📚 Courses:
• BA
• LLB
• BJMC

🧠 Skills:
Creativity, Communication"""

        # 📊 SKILLS
        elif "skill" in msg:
            reply = """🔥 Top Skills (All Fields):
• Communication
• Problem Solving
• Critical Thinking
• Coding (for tech)
• Excel / Data Analysis

💡 Tip: Learn 1 hard skill + 1 soft skill"""

        # 📄 RESUME
        elif "resume" in msg:
            reply = """📄 Resume Tips:
• Keep it 1 page
• Add projects + skills
• Use simple format
• Highlight achievements
• No spelling mistakes"""

        # 📊 SKILL GAP
        elif "gap" in msg:
            reply = """📊 Skill Gap:
👉 Compare:
Your skills VS Required skills

💡 Improve by:
• Online courses
• Practice
• Projects"""

        # 📚 COURSES
        elif "course" in msg:
            reply = """📚 Best Platforms:
• Coursera
• Udemy
• NPTEL
• YouTube

💡 Tip: Choose skill-based courses"""

        # 🧠 DEFAULT SMART RESPONSE
        else:
            reply = """🤖 I can help with:
• Career options
• Courses
• Skills
• Resume
• Skill gap

👉 Try asking:
"Best career for PCM"
"Courses after commerce"
"How to improve skills"
"""

    except Exception as e:
        reply = "⚠️ Something went wrong"

    return jsonify({"reply": reply})
# ================= SKILL GAP =================
@app.route("/skill_gap", methods=["GET", "POST"])
@login_required
def skill_gap():

    if request.method == "POST":

        user_input = request.form["your_skills"]

        # split + normalize
        raw_skills = user_input.split(",")
        user_skills = normalize_skills(raw_skills)

        # detect career
        career = detect_best_career(user_skills)

        # 🔥 STEP E (STREAM FALLBACK)
        if not career:
            for stream, skills in stream_skills.items():
                if any(skill in user_skills for skill in skills):
                    career = stream + " related field"
                    required_skills = skills
                    break

        # required skills
        if career in career_details:
            required_skills = [s.lower() for s in career_details[career]["skills"]]
        elif "required_skills" not in locals():
            required_skills = ["problem solving", "communication"]

        # missing
        missing_skills = get_missing_skills(user_skills, required_skills)

        matched = len(required_skills) - len(missing_skills)
        total = len(required_skills)
        score = int((matched / total) * 100)

        # 🎯 SKILL LEVEL BADGE (FIX: inside POST)
        if score >= 80:
            level = "Expert"
        elif score >= 50:
            level = "Intermediate"
        else:
            level = "Beginner"

        # 🔥 SMART SUGGESTIONS (FIX: duplicate removed)
        suggestions = []

        for skill in missing_skills:
            if skill == "python":
                suggestions.append("Learn Python from Coursera / YouTube")
            elif skill == "ml":
                suggestions.append("Start Machine Learning with Scikit-learn")
            elif skill == "sql":
                suggestions.append("Practice SQL on LeetCode / HackerRank")
            elif skill == "excel":
                suggestions.append("Learn Excel for data analysis")
            elif skill == "communication":
                suggestions.append("Improve communication via public speaking")
            else:
                suggestions.append(f"Learn {skill} from online courses")

        # priority split
        # priority split
        high_priority = []
        low_priority = []

        for skill in missing_skills:
            if skill in ["communication", "problem solving", "logic"]:
                 high_priority.append(skill)
            else:
                low_priority.append(skill)

# ✅ ADD HERE (LOOP के बाहर)
        session["missing_skills"] = missing_skills
        session["career"] = career
        session["level"] = level
        session["user_skills"] = user_skills

        # ✅ FINAL RETURN (correct position)
        session["skill_gap_data"] = {
            "required_skills": required_skills,
            "user_skills": user_skills,
            "missing_skills": missing_skills,
            "high_priority": high_priority,
            "low_priority": low_priority,
            "suggestions": suggestions,
            "score": score,
            "level": level,
            "career": career
        }

        return redirect(url_for("skill_gap"))

    data = session.get("skill_gap_data")

    if data:
        return render_template("skill_gap.html", **data)

    return render_template("skill_gap.html")

@app.route("/courses")
@login_required
def courses():

    career = session.get("career")
    missing_skills = session.get("missing_skills", [])
    user_skills = session.get("user_skills", [])

    recommended_courses = []

    career_lower = career.lower() if career else ""

    # ================= USER SKILLS FILTER =================
    for skill in user_skills:

        if not skill:
            continue

        skill_lower = skill.lower().strip()

        if skill_lower in course_data:
            recommended_courses.extend(course_data[skill_lower])

    # ================= MISSING SKILLS FILTER =================
    for skill in missing_skills:

        if not skill:
            continue

        skill_lower = skill.lower().strip()

        if skill_lower in course_data:
            recommended_courses.extend(course_data[skill_lower])

    # ================= STREAM FILTER =================
    combined_skills = user_skills + missing_skills

    stream = detect_stream(combined_skills)

    if stream and stream in stream_courses:
        recommended_courses.extend(stream_courses[stream])

    # ================= CAREER FILTER =================
    if career_lower:

        for key in course_data:

            if career_lower in key.lower():
                recommended_courses.extend(course_data[key])

    # ================= VIEW ALL =================
    if request.args.get("all") == "true":

        recommended_courses = []

        for course_list in course_data.values():
            recommended_courses.extend(course_list)

        for course_list in stream_courses.values():
            recommended_courses.extend(course_list)

        recommended_courses.extend(all_courses)

    # ================= REMOVE DUPLICATES =================
    unique_courses = []
    seen = set()

    for course in recommended_courses:

        name = course.get("name")

        if name and name not in seen:
            unique_courses.append(course)
            seen.add(name)

    # ================= FALLBACK =================
    if not unique_courses:
        unique_courses = all_courses[:15]

    return render_template("courses.html", courses=unique_courses)


@app.route("/admin")
@admin_required
def admin():

    
    conn = get_db_connection()
    cursor = conn.cursor()
    # Total users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # Total predictions
    cursor.execute("SELECT COUNT(*) FROM history")
    total_predictions = cursor.fetchone()[0]

    # Most recommended career
    cursor.execute("""
        SELECT career, COUNT(*) as count
        FROM history
        GROUP BY career
        ORDER BY count DESC
        LIMIT 1
    """)
    most_career = cursor.fetchone()

    if most_career:
        most_career_name = most_career[0]
        most_career_count = most_career[1]
    else:
        most_career_name = "No Data"
        most_career_count = 0


    # Graph data
    cursor.execute("""
        SELECT career, COUNT(*)
        FROM history
        GROUP BY career
    """)
    data = cursor.fetchall()


    # Career list data
    cursor.execute("""
        SELECT career, COUNT(*)
        FROM history
        GROUP BY career
    """)
    career_data = cursor.fetchall()

    conn.close()


    careers = [row[0] for row in data]
    counts = [row[1] for row in data]


    return render_template(
        "admin.html",
        total_users=total_users,
        total_predictions=total_predictions,
        most_career_name=most_career_name,
        most_career_count=most_career_count,
        careers=careers,
        counts=counts,
        career_data=career_data
    )



def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(debug=True)
