import re
import string
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def clean_text(text):
    """
    Cleans the text by:
    1. Converting to lowercase
    2. Removing punctuation
    3. Removing stopwords
    """
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    stop_words = set(stopwords.words('english'))
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words]
    return " ".join(filtered_words)

def rank_resumes(job_description, resume_texts, candidate_names):
    """
    Calculates the similarity score between the Job Description and each Resume.
    Returns a Pandas DataFrame with Rank, Candidate, and Match Score.
    """
    cleaned_jd = clean_text(job_description)
    cleaned_resumes = [clean_text(text) for text in resume_texts]
    all_documents = [cleaned_jd] + cleaned_resumes
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_documents)
    
    jd_vector = tfidf_matrix[0:1]
    resume_vectors = tfidf_matrix[1:]
    
    similarity_scores = cosine_similarity(jd_vector, resume_vectors).flatten()
    
    results = []
    for i, score in enumerate(similarity_scores):
        results.append({
            "Candidate": candidate_names[i],
            "Match Score": round(score * 100, 2)
        })
    
    df = pd.DataFrame(results)
    df = df.sort_values(by="Match Score", ascending=False)
    df["Rank"] = range(1, len(df) + 1)
    df = df[["Rank", "Candidate", "Match Score"]]
    
    return df