import joblib
from sentence_transformers import SentenceTransformer
    
model=joblib.load("models/log_classifier.joblib")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def classify_with_bert(log_message):
    embedding = embedding_model.encode([log_message])
    proba = model.predict_proba(embedding)[0]
    if max(proba)<0.5:
        predicted_label="Unclassified"
    else:
        predicted_label = model.predict(embedding)[0]
    return str(predicted_label)
