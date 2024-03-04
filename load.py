import pandas as pd
import joblib

# Load the pre-trained SVM model
svm_clf = joblib.load('svm_model.pkl')

# Load the fitted CountVectorizer
vectorizer = joblib.load('count_vectorizer.pkl')

# Transform the new text data using the loaded CountVectorizer
X_test_vec = vectorizer.transform(["The service was good ! i really loved it!"])

# Make predictions using the loaded model
y_pred = svm_clf.predict(X_test_vec)
print("Predicted sentiment:", y_pred)
