# 🧠 Log Classifier API

This project is a FastAPI-based microservice that classifies log messages into target labels using three different strategies:
- 🧾 Rule-based classification with **regular expressions**
- 🤖 ML-based classification using **BERT + Logistic Regression**
- 🧠 Contextual classification using a **Large Language Model (LLM)**

---

# 🧪 Classification Pipeline

1. 🔍 Regex-based Classifier
- Uses predefined regular expressions
- Ideal for simple, pattern-matching use cases
2. 🤖 BERT + Logistic Regression
- Uses bert-base-uncased from HuggingFace for embeddings
- Logistic regression is trained over vectorized representations
- Good balance of accuracy and speed
3. 💬 LLM-based Classification
- Leverages a powerful LLM (e.g., OpenAI GPT, Azure OpenAI)
- Best for nuanced, free-form logs with complex semantics
- Requires API access and secret key set via .env


#   📁 Project Structure
├── server.py               # FastAPI app

├── classify.py           # Core classification logic

├── processor_regex.py              # Regex

├── processor_bert.py               # BERT

├── processor_llm.py                # LLM

├── models/

│   ├── log_classifier.joblib

├── resources/            # Temporary storage for CSVs

│   ├── test.csv

├── training/

│   ├── training.ipynb

│   ├── dataset/

│   ├──  │   ├── synthetic_logs.csv

├── requirements.txt

└── README.md



# Installation
```bash
git clone https://github.com/Dhanjith01/log-classification.git
cd log-classification
pip install -r requirements.txt
```

# Running the API
```bash
uvicorn server:app --reload
```
## Request
Upload a .csv file with the following columns:
- source: the source system/service
- log_message: the log text to classify
## Response
Returns a new CSV file with a third column: target_label





