import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle

# Load dataset
data = pd.read_csv("dataset/career_data_100k_advanced.csv")

# NEW FEATURES (ADD THIS)
data["Tech_Strength"] = (data["Technical_Skill_Score"] + data["Math_Score"]) / 2

data["Soft_Strength"] = (data["Communication_Score"] + data["Creativity_Score"]) / 2

data["Overall_Score"] = (
    data["Math_Score"] +
    data["Technical_Skill_Score"] +
    data["Communication_Score"] +
    data["Creativity_Score"] +
    data["Aptitude_Score"]
) / 5

# Create encoders
le_stream = LabelEncoder()
le_interest = LabelEncoder()
le_skill = LabelEncoder()
le_career = LabelEncoder()

# Encode categorical columns
data["Stream"] = le_stream.fit_transform(data["Stream"])
data["Interest"] = le_interest.fit_transform(data["Interest"])
data["Skill_Level"] = le_skill.fit_transform(data["Skill_Level"])
data["Recommended_Career"] = le_career.fit_transform(data["Recommended_Career"])

# Features & Target
X = data[[
    "Stream",
    "Interest",
    "Math_Score",
    "Communication_Score",
    "Technical_Skill_Score",
    "Creativity_Score",
    "Aptitude_Score",
    "Skill_Level",
    "Tech_Strength",
    "Soft_Strength",
    "Overall_Score"
]]
y = data["Recommended_Career"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

# 🔥 TRAIN MODEL (MUST ADD)
model.fit(X_train, y_train)

# 🔥 PREDICT
y_pred = model.predict(X_test)

from sklearn.metrics import accuracy_score
print("Model Accuracy:", accuracy_score(y_test, y_pred))

# Save everything
pickle.dump(model, open("career_model.pkl", "wb"))
pickle.dump(le_stream, open("le_stream.pkl", "wb"))
pickle.dump(le_interest, open("le_interest.pkl", "wb"))
pickle.dump(le_skill, open("le_skill.pkl", "wb"))
pickle.dump(le_career, open("le_career.pkl", "wb"))

print("Model & encoders saved successfully!")