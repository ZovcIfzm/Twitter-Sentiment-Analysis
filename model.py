# Base code from tutorial:
#https://www.pluralsight.com/guides/building-a-twitter-sentiment-analysis-in-python

import pandas as pd
import numpy as np
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

# ML Libraries
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

# Extra
import time

# Global Parameters
stop_words = set(stopwords.words('english'))

# Loading dataset
def load_dataset(filename, cols):
    dataset = pd.read_csv(filename, encoding='latin-1')
    dataset.columns = cols
    return dataset

# Dataset has 6 columns, we only want 2- for scalability we need to remove unwanted cols
def remove_unwanted_cols(dataset, cols):
    for col in cols:
        del dataset[col]
    return dataset

# We need to preprocess data into a form we want
def preprocess_tweet_text(tweet):
    # Convert to all lowercase
    tweet.lower()
    # Remove urls
    tweet = re.sub(r"http\S+|www\S+|https\S+", '', tweet, flags=re.MULTILINE)
    # Remove user @ references and '#' from tweet
    tweet = re.sub(r'\@\w+|\#','', tweet)
    # Remove punctuations
    tweet = tweet.translate(str.maketrans('', '', string.punctuation))
    # Remove stopwords
    tweet_tokens = word_tokenize(tweet)
    filtered_words = [w for w in tweet_tokens if not w in stop_words]
    
    # Stemmer, removing parts like "ing"
    ps = PorterStemmer()
    stemmed_words = [ps.stem(w) for w in filtered_words]
    #lemmatizer = WordNetLemmatizer()
    #lemma_words = [lemmatizer.lemmatize(w, pos='a') for w in stemmed_words]
    
    return " ".join(stemmed_words)

# Vectorizes data, converting tokens into numbers
def get_feature_vector(train_fit):
    vector = TfidfVectorizer(sublinear_tf=True)
    vector.fit(train_fit)
    return vector

# Unused within program, but this allows us to know
# What "sentiment" values actually mean
def int_to_string(sentiment):
    if sentiment == 0:
        return "Negative"
    elif sentiment == 2:
        return "Neutral"
    else:
        return "Positive"

# Load dataset
load_start = time.time()
dataset = load_dataset("data/training.csv", ['target', 't_id', 'created_at', 'query', 'user', 'text'])
load_end = time.time()

# Remove unwanted columns from dataset
n_dataset = remove_unwanted_cols(dataset, ['t_id', 'created_at', 'query', 'user'])
#Preprocess data
dataset.text = dataset['text'].apply(preprocess_tweet_text)
# Split dataset into Train, Test

# Same tf vector will be used for Testing sentiments on unseen trending data
tf_vector = get_feature_vector(np.array(dataset.iloc[:, 1]).ravel())
X = tf_vector.transform(np.array(dataset.iloc[:, 1]).ravel())
y = np.array(dataset.iloc[:, 0]).ravel()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=30)

# Training Naive Bayes model
nb_start = time.time()
NB_model = MultinomialNB()
NB_model.fit(X_train, y_train)
y_predict_nb = NB_model.predict(X_test)
print(accuracy_score(y_test, y_predict_nb))
nb_end = time.time()

# Training Logistics Regression model
lr_start = time.time()
LR_model = LogisticRegression(solver='lbfgs', max_iter=100)
LR_model.fit(X_train, y_train)
y_predict_lr = LR_model.predict(X_test)
print(accuracy_score(y_test, y_predict_lr))
lr_end = time.time()

print("time dif:")
print("load: ", load_end-load_start) 
print("bayes: ", nb_end-nb_start)
print("logreg: ", lr_end-lr_start)

# Printed results (lbfgs failed to converge):
# 0.768521875
# 0.787809375

# With stemmer (lbfgs failed to converge):
# 0.762571875
# 0.782196875
# load:  10.33156943321228 (seconds)
# bayes:  0.7680816650390625 (seconds)
# logreg:  37.22610831260681 (seconds)
