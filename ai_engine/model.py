# model.py — TF-IDF + SVM (much better than Naive Bayes)

import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        ngram_range=(1, 3),
        min_df=1,
        sublinear_tf=True,
    )),
    ('svm', LinearSVC(C=1.0, max_iter=2000))
])

def train(X, y):
    pipeline.fit(X, y)
    with open("ai_engine/model.pkl", "wb") as f:
        pickle.dump(pipeline, f)

def load_model():
    with open("ai_engine/model.pkl", "rb") as f:
        return pickle.load(f)