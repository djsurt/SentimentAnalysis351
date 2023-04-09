import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
from joblib import dump

# Load and preprocess data
data = pd.read_csv("preprocessed_insults_dataset.csv")
data.dropna(inplace=True)

# Create TfidfVectorizer
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(data['Comment'])
y = data['Label']

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
classifier = MultinomialNB()
classifier.fit(X_train, y_train)

# Evaluate the model
y_pred = classifier.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
dump(classifier, 'malicious_tweet_classifier.joblib')
dump(vectorizer, 'tfidf_vectorizer.joblib')
