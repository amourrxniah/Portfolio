import sys
import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import pickle
import nltk
nltk.download('punkt')
nltk.download('stopwords')

from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, 
                            QTextEdit, QPushButton, QVBoxLayout, 
                            QWidget, QMessageBox)

class SpamClassifierApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_model()
        
    def initUI(self):
        self.setWindowTitle('Spam/Ham Classifier')
        self.setGeometry(100, 100, 500, 400)
        
        layout = QVBoxLayout()
        
        self.label = QLabel('Enter your message:')
        layout.addWidget(self.label)
        
        self.text_input = QTextEdit()
        layout.addWidget(self.text_input)
        
        self.classify_btn = QPushButton('Classify')
        self.classify_btn.clicked.connect(self.classify_message)
        layout.addWidget(self.classify_btn)
        
        self.result_label = QLabel('Result will appear here')
        layout.addWidget(self.result_label)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def load_model(self):
        try:
            # Try to load pre-trained model
            with open('spam_model.pkl', 'rb') as f:
                self.model = pickle.load(f)
            with open('vectorizer.pkl', 'rb') as f:
                self.vectorizer = pickle.load(f)
        except:
            # If no model exists, train a new one
            self.train_model()
    
    def train_model(self):
        # Load dataset (you should replace this with your actual dataset)
        # For demo purposes, we'll create a small dummy dataset
        data = {
            'text': [
                'Free money now!!!', 'Hi John, how are you?',
                'Win a prize today!', 'Meeting at 3pm tomorrow',
                'Claim your reward', 'Lunch tomorrow?'
            ],
            'label': ['spam', 'ham', 'spam', 'ham', 'spam', 'ham']
        }
        df = pd.DataFrame(data)
        
        # Preprocess text
        df['processed_text'] = df['text'].apply(self.preprocess_text)
        
        # Vectorize text
        self.vectorizer = TfidfVectorizer(max_features=1000)
        X = self.vectorizer.fit_transform(df['processed_text'])
        y = df['label']
        
        # Train model
        self.model = MultinomialNB()
        self.model.fit(X, y)
        
        # Save model for future use
        with open('spam_model.pkl', 'wb') as f:
            pickle.dump(self.model, f)
        with open('vectorizer.pkl', 'wb') as f:
            pickle.dump(self.vectorizer, f)
    
    def preprocess_text(self, text):
        # Tokenize
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and non-alphabetic tokens
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
        
        # Stemming
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(word) for word in tokens]
        
        return ' '.join(tokens)
    
    def classify_message(self):
        message = self.text_input.toPlainText()
        if not message.strip():
            QMessageBox.warning(self, 'Warning', 'Please enter a message to classify.')
            return
        
        # Preprocess and vectorize the message
        processed = self.preprocess_text(message)
        vectorized = self.vectorizer.transform([processed])
        
        # Predict
        prediction = self.model.predict(vectorized)[0]
        probability = self.model.predict_proba(vectorized).max()
        
        self.result_label.setText(f'Result: {prediction} (confidence: {probability:.2f})')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SpamClassifierApp()
    window.show()
    sys.exit(app.exec_())