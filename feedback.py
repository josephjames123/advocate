import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
import joblib
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

df = pd.read_csv('feedback_dataset.csv')

def preprocess_text(text):
    text = text.lower()  
    text = re.sub(r'[^\w\s]', '', text) 
    tokens = word_tokenize(text)  
    stop_words = set(stopwords.words('english')) 
    filtered_tokens = [word for word in tokens if word not in stop_words]  
    return ' '.join(filtered_tokens)

df['feedback_text'] = df['feedback_text'].apply(preprocess_text)

df.drop_duplicates(inplace=True)

X_train, X_test, y_train, y_test = train_test_split(df['feedback_text'], df['sentiment'], test_size=0.2, random_state=42)

vectorizer = CountVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

svm_clf = SVC(kernel='linear') 
svm_clf.fit(X_train_vec, y_train)

joblib.dump(svm_clf, 'svm_model.pkl')

y_pred = svm_clf.predict(X_test_vec)

accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)
print("Classification Report:")
print(classification_report(y_test, y_pred))
