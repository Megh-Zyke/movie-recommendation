from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
from googleImages import search_images
import joblib


app = Flask(__name__)
CORS(app) 


df = pd.read_csv("exports/final_movie.csv")
df = df.iloc[:, 1:]
api_key = ""


with open('exports/movie_names.pkl', 'rb') as file:
    movie_titles = pickle.load(file)
    titles = movie_titles

def get_recommendation(movie):
    movie = movie.lower()
    if movie in titles:
        sig_scores = sorted(list(enumerate(sig[titles.index(movie)])), key=lambda x: x[1], reverse=True)
        sig_scores = sig_scores[1:10]
        movie_indices = [i[0] for i in sig_scores]
        return df['movie_title'].iloc[movie_indices]
    else :
        return "No movie present of the sort"

with open('exports/movie_posters.pkl', 'rb') as file:
    movie_posters = pickle.load(file)

sig = joblib.load('exports/sig_scores.pkl')

movie_titles = [x.title() for x in movie_titles]

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        'titles': movie_titles
    }
    return jsonify(data)

@app.route('/api/data/movie', methods=['POST'])
def get_posters():
    data = request.json
    movies_list = data.get('movies', '')
    movies = []
    for movie in movies_list:
        movies.append([movie, movie_posters[movie_titles.index(movie)]])
    
    data = {
        'movies': movies
    }
    return jsonify(data), 200

@app.route('/api/get-movie-info', methods=['POST'])
def get_movie():
    data = request.json
    message = data.get('message', '').strip()
    
    movie_exists = message.title() in movie_titles

    response = {
        'exists': movie_exists,
        'name': message.title() if movie_exists else 'Movie not found',
        'poster': movie_posters[movie_titles.index(message.title())] if movie_exists else ''
    }

    return jsonify(response), 200

@app.route('/api/get-movie', methods=['GET'])
def get_movie_by_name():
    movie_name = request.args.get('name', '').strip()
    
    # Find the index of the movie in the DataFrame
    index_list = df[df['movie_title'].str.lower() == movie_name.lower()].index.tolist()
    
    if not index_list:
        return jsonify({'error': 'Movie not found locally'}), 404
    
    index = index_list[0]

    session = requests.Session()
    retries = Retry(
        total=5, 
        backoff_factor=1,  
        status_forcelist=[429, 500, 502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try: 
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_name}"
        response = session.get(search_url)
        response.raise_for_status()
        data = response.json()

        if data['results']:
            movie = data['results'][0]
            movie_id = movie['id']

            movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
            movie_response = session.get(movie_url)
            movie_response.raise_for_status()
            movie_data = movie_response.json()
        else:
            return jsonify({'error': 'Movie not found in external API'}), 404
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

    
    recommendations = list(get_recommendation(movie_name))
    rec = {}
    for recomend in recommendations:
        rec[recomend] = movie_posters[movie_titles.index(recomend.title())]
    print(rec)
    response = {
        'movieInfo': movie_data,
        'castDetails': {
            'director': [df.iloc[index, 0] , search_images(df.iloc[index, 0] )],
            'actor-1': [df.iloc[index, 1] , search_images(df.iloc[index, 1])],
            'actor-2': [df.iloc[index, 2] , search_images(df.iloc[index, 2])],
            'actor-3': [df.iloc[index, 3] , search_images(df.iloc[index, 3])]
        }
        ,
        'recommendations': rec
    }
    print(index)
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)
