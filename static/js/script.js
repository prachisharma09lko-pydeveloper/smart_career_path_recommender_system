// 🔹 Dynamic Background Based on Page
const pageBackgrounds = {
    "index.html": "images/home.jpg",
    "login.html": "images/login.jpg",
    "register.html": "images/register.jpg",
    "dashboard.html": "images/dashboard.jpg",
    "recommendation.html": "images/recommend.jpg",
    "skill-gap.html": "images/skill.jpg",
    "courses.html": "images/course.jpg",
    "admin.html": "images/admin.jpg"
};


const currentPage = window.location.pathname.split("/").pop();

if (pageBackgrounds[currentPage]) {
    document.body.style.background = `url(${pageBackgrounds[currentPage]}) no-repeat center center/cover`;
}

// 🔹 Recommendation Logic
function recommendCareer() {
    let skill = document.getElementById("skills").value;
    let result = document.getElementById("result");

    if (skill === "programming") {
        result.innerHTML = "💻 Recommended Career: Software Developer";
    } else if (skill === "design") {
        result.innerHTML = "🎨 Recommended Career: UI/UX Designer";
    } else if (skill === "analysis") {
        result.innerHTML = "📊 Recommended Career: Data Analyst";
    } else {
        result.innerHTML = "⚡ Please select a skill.";
    }
}

// 🔹 Skill Gap Analysis
function analyzeSkillGap() {
    let career = document.getElementById("career").value;
    let gap = document.getElementById("gapResult");

    gap.innerHTML = `To become a ${career}, improve communication, problem-solving & practical skills.`;
}

// 🔹 Course Suggestion
function suggestCourse() {
    let course = document.getElementById("courseResult");
    course.innerHTML = `
        📚 Suggested Courses:
        <br> • Python Programming
        <br> • Data Structures
        <br> • Communication Skills
    `;
}

// 🔹 Back Button
function goBack() {
    window.history.back();
}
