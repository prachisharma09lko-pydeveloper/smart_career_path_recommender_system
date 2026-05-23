import pandas as pd

# Load dataset
data = pd.read_csv("students.csv")

# Show first 5 rows
print(data.head())

# Show total rows and columns
print(data.shape)
