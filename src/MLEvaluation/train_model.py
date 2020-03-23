import csv
from pymongo import MongoClient
import os
import json
import pandas as pd
import numpy as np
import pickle

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.model_selection import KFold, train_test_split
from sklearn import metrics

from src.MLEvaluation.features import WebsiteInfo

def build_model():
    # Set up MongoDB connection
    client = MongoClient('localhost', 27017)
    db = client['phishing_training_data']
    websites = db.websites

    df = pd.DataFrame(list(websites.find()))

    df = df.sample(frac=1)  # shuffle the rows

    one_hot_protocol = pd.get_dummies(df['protocol'], columns=['protocol'])
    df = pd.concat([df, one_hot_protocol], axis=1)
    one_hot_protocol = pd.get_dummies(df['cert_auth'], columns=['cert_auth'])
    df = pd.concat([df, one_hot_protocol], axis=1)
    feature_columns = list(df.columns)
    feature_columns.remove('is_legit')
    feature_columns.remove('_id')
    feature_columns.remove('protocol')
    feature_columns.remove('url')
    feature_columns.remove('path')
    feature_columns.remove('query')
    feature_columns.remove('fragment')
    feature_columns.remove('cert_auth')
    feature_columns.remove('target_url')
    feature_columns.remove('unknown_url')
    feature_columns.remove('keyword')

    features = df[feature_columns]
    target_variable = df.is_legit

    print('\nRandom Forest Results:')
    rf = RandomForest(features, feature_columns, target_variable)
    rf.predict_test_set()

    print('Pickling random forest')
    with open(os.path.join(os.getcwd(), 'models\\random_forest.pkl'), 'wb') as random_forest_output:
        pickle.dump(rf, random_forest_output, pickle.HIGHEST_PROTOCOL)
    
    client.close()

class ClassificationModel:
    def __init__(self, features, feature_columns, target_variables, classifier):
        self.features = features
        self.feature_columns = feature_columns
        self.target_variable = target_variables

        self.features_train, self.features_test, self.target_train, self.target_test = train_test_split(
            self.features, self.target_variable, test_size=.4, random_state=42)
        self.clf = classifier.fit(self.features_train, self.target_train)

    def predict_test_set(self):
        target_predictions = self.clf.predict(self.features_test)
        feature_predictions = self.clf.predict(self.features_train)
        print(
            f"Train Accuracy: {metrics.accuracy_score(self.target_train, feature_predictions)}")
        print(
            f"Train Precision: {metrics.precision_score(self.target_train, feature_predictions)}")
        print(
            f"Train Recall: {metrics.recall_score(self.target_train, feature_predictions)}")
        print(
            f"Test Accuracy: {metrics.accuracy_score(self.target_test, target_predictions)}")
        print(
            f"Test Precision: {metrics.precision_score(self.target_test, target_predictions)}")
        print(
            f"Test Recall: {metrics.recall_score(self.target_test, target_predictions)}")
        print(
            f"\nTrain Confusion Matrix: \n {metrics.confusion_matrix(self.target_train, feature_predictions)}")
        print(
            f"\nTest Confusion Matrix: \n {metrics.confusion_matrix(self.target_test, target_predictions)}")
        print(
            f"\nTrain Label Count Actual:\n{self.target_train.value_counts()}")
        print(f"\nTest Label Count Actual:\n{self.target_test.value_counts()}")

    def predict_url(self, url: str, keyword: str):
        u = WebsiteInfo(url, keyword).to_json()
        url_df = pd.DataFrame.from_records([u])
        one_hot_protocol = pd.get_dummies(url_df['protocol'], columns=['protocol'])
        url_df = pd.concat([url_df, one_hot_protocol], axis=1)
        one_hot_protocol = pd.get_dummies(url_df['cert_auth'], columns=['cert_auth'])
        url_df = pd.concat([url_df, one_hot_protocol], axis=1)
        url_features = url_df[self.feature_columns]
        target_prediction = self.clf.predict(url_features)
        class_probabilities = self.clf.predict_proba(url_features)
        print(f'Predictions for {url}: {target_prediction[0]}')
        return (u, target_prediction[0], np.max(class_probabilities))

    def fit_classifier(self, url: str,  keyword: str, label):
        u = WebsiteInfo(url, keyword).to_json()
        url_df = pd.DataFrame.from_records([u])
        one_hot_protocol = pd.get_dummies(url_df['protocol'], columns=['protocol'])
        url_df = pd.concat([url_df, one_hot_protocol], axis=1)
        one_hot_protocol = pd.get_dummies(url_df['cert_auth'], columns=['cert_auth'])
        url_df = pd.concat([url_df, one_hot_protocol], axis=1)
        url_df['http'] = 1 if url_df.iloc[0]['protocol'] == 'http' else 0
        url_df['https'] = 1 if url_df.iloc[0]['protocol'] == 'https' else 0
        url_features = url_df[self.feature_columns]
        self.clf.fit(url_features, [label])

class RandomForest(ClassificationModel):
    def __init__(self, features, feature_columns, target_variable):
        clf = RandomForestClassifier(n_estimators=100)
        super().__init__(features, feature_columns, target_variable, clf)

if __name__ == "__main__":
    build_model()