import joblib
import pickle
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

df1 = pd.read_csv('exports/final_movie.csv')

sig = joblib.load('exports/sig_scores.pkl')
with open('exports/movie_names.pkl', 'rb') as file:
    titles = pickle.load(file)


def get_recommendation(movie):
    movie = movie.lower()
    if movie in titles:
        sig_scores = sorted(list(enumerate(sig[titles.index(movie)])), key=lambda x: x[1], reverse=True)
        sig_scores = sig_scores[1:11]
        movie_indices = [i[0] for i in sig_scores]
        return df1['movie_title'].iloc[movie_indices]
    else :
        return "No movie present of the sort"


