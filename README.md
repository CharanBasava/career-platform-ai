# Semantic Skill Equivalence Detection System
### Transformer-Based Recruitment Intelligence using Sentence-BERT

---

## Overview

This project is an AI-powered recruitment system that detects **semantic equivalence between candidate skills and job requirements** using transformer-based NLP models.

Unlike traditional keyword-based systems, this approach understands the **context and meaning of skills**, improving matching accuracy and reducing hiring inefficiencies.

---
## 🎥 Project Demo

[▶️ Watch Demo Video](./semantic-project-demo.mp4)

## Problem Statement

Traditional recruitment systems suffer from:

- Keyword dependency (fails on synonyms)
- High false rejection rates
- Poor semantic understanding
- Manual screening inefficiencies

---

## Solution

This system uses **Sentence-BERT embeddings** to:

- Detect equivalent and similar skills
- Perform skill gap analysis
- Match candidates to jobs
- Predict salary insights
- Generate AI-based interview responses

---

## System Architecture

### Pipeline

1. Data Ingestion  
   - Resume parsing (PDF/DOCX)  
   - Job description extraction  

2. Preprocessing  
   - Text normalization  
   - Tokenization  

3. Semantic Embedding  
   - Sentence-BERT (all-MiniLM-L6-v2)  

4. Similarity Engine  
   - Cosine similarity  
   - Threshold-based classification  

5. Dual-Track Matching  
   - Job Title Matching  
   - Skill-Based Matching  

6. Prediction Layer  
   - Skill classification  
   - Salary prediction (XGBoost)  

7. AI Layer  
   - Interview-style response generation  

---

## Tech Stack

- Backend: Flask (Python)
- NLP: Sentence-Transformers (SBERT)
- ML: Scikit-learn, XGBoost
- Data: Pandas, NumPy
- Parsing: PyMuPDF, python-docx
- LLM: Llama 3.1 (Groq API)
- API: Adzuna Job API

---

## Dataset

- 1000 skill pairs  
- 500 equivalent  
- 500 non-equivalent  

### Categories

- Direct Synonym  
- Acronym  
- Hierarchical Overlap  
- Lexical Trap  
- Semantic Negative  

### Split

- 70% Training  
- 15% Validation  
- 15% Testing  

---

## Models

### Baseline Models

- Keyword Matching  
- TF-IDF + Cosine Similarity  

### Proposed Model

- Sentence-BERT (Pretrained)  
- Cosine similarity classification  

---

## Results

### Benchmark Performance

| Model | Accuracy | F1 Score |
|------|--------|---------|
| Keyword Matching | 40.7% | 0.28 |
| TF-IDF | 59.3% | 0.37 |
| SBERT | 79.1% | 0.78 |

### Final System Performance

- Accuracy: 88.67%  
- Precision: 87.45%  
- Recall: 86.92%  
- F1 Score: 87.18%  
- Inference Time: ~2.3s  

---

## Key Features

- Semantic skill equivalence detection  
- Dual-track job matching system  
- Explainable similarity scoring  
- AI-powered interview assistant  
- Salary prediction module  
- End-to-end recruitment pipeline  

---


### Features Used

- Skills  
- Experience  
- Job type  
- Company size  

---

## Limitations

- Small dataset  
- Synthetic data  
- No real-world validation  
- Threshold sensitivity  
- Limited scalability  

---

## Future Work

- Fine-tune SBERT on real datasets  
- Integrate BERT/GPT hybrid models  
- Real-time job market integration  
- Cloud deployment (AWS/GCP)  
- Multi-language support  

---

## How to Run

```bash
# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
python run.py
