import pandas as pd
import random

# Total students
num_students = 100000

# Streams
streams = ["Computer Science", "Biology", "Commerce", "Arts"]

# Interests by stream
interests = {
    "Computer Science": ["AI", "Web", "Data", "Cybersecurity"],
    "Biology": ["Medical", "Research", "Genetics"],
    "Commerce": ["Finance", "Marketing", "Accounting"],
    "Arts": ["Design", "Writing", "Psychology"]
}

data = []

for i in range(1, num_students + 1):
    
    stream = random.choice(streams)
    interest = random.choice(interests[stream])
    
    math_score = random.randint(40, 100)
    communication_score = random.randint(35, 100)
    technical_score = random.randint(30, 100)
    creativity_score = random.randint(30, 100)
    aptitude_score = random.randint(40, 100)
    
    # Skill Level Logic
    if aptitude_score > 80:
        skill_level = "Advanced"
    elif aptitude_score >= 60:
        skill_level = "Intermediate"
    else:
        skill_level = "Beginner"
    
    # Career Mapping Logic (Advanced)
    if stream == "Computer Science" and technical_score > 75 and math_score > 70:
        career = "Machine Learning Engineer"
    elif stream == "Computer Science" and interest == "Web":
        career = "Web Developer"
    elif stream == "Biology" and interest == "Medical":
        career = "Doctor"
    elif stream == "Commerce" and communication_score > 75:
        career = "Marketing Manager"
    elif stream == "Arts" and creativity_score > 80:
        career = "Graphic Designer"
    else:
        career = "Career Counselor"
    
    data.append([
        i, stream, interest, math_score, communication_score,
        technical_score, creativity_score, aptitude_score,
        skill_level, career
    ])

columns = [
    "Student_ID", "Stream", "Interest", "Math_Score",
    "Communication_Score", "Technical_Skill_Score",
    "Creativity_Score", "Aptitude_Score",
    "Skill_Level", "Recommended_Career"
]

df = pd.DataFrame(data, columns=columns)

df.to_csv("career_data_100k_advanced.csv", index=False)

print("Dataset Generated Successfully ✅")
