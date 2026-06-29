import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Sample training data
data = {
    "text": [
        "There is no electricity in my area",
        "Water supply is not working",
        "Big potholes on road",
        "Hospital has no oxygen",
        "Bribe taken by officer",
        "Street light not working",
        "Drain water overflow",
        "Road broken due to rain",
        "Ambulance not available",
        "Fraud in government scheme"
    ],
    "category": [
        "Electricity",
        "Water",
        "Road",
        "Health",
        "Corruption",
        "Electricity",
        "Water",
        "Road",
        "Health",
        "Corruption"
    ]
}

df = pd.DataFrame(data)

# Create ML pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", LogisticRegression())
])

# Train model
model.fit(df["text"], df["category"])

# Save model
joblib.dump(model, "category_model.pkl")

print("Model trained and saved successfully!")