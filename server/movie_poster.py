import requests
import pickle
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load movie titles
with open('exports/movie_names.pkl', 'rb') as file:
    movie_titles = pickle.load(file)


movie_poster_links = []

def get_movie_poster(movie_title, api_key=""):
    session = requests.Session()
    
    retries = Retry(
        total=5, 
        backoff_factor=1,  
        status_forcelist=[429, 500, 502, 503, 504]  
    )
    
    session.mount("https://", HTTPAdapter(max_retries=retries))
    
    try:
        # Search for the movie by title
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
        search_response = session.get(search_url)
        search_response.raise_for_status()  # Raise an error for bad status codes
        search_data = search_response.json()

        if search_data['results']:
            # Get the first movie result
            movie = search_data['results'][0]
            movie_id = movie['id']

            # Get movie details by movie ID
            movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
            movie_response = session.get(movie_url)
            movie_response.raise_for_status()  # Raise an error for bad status codes
            movie_data = movie_response.json()

            # Get the poster path
            poster_path = movie_data.get('poster_path')
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                return poster_url
            else:
                return "No poster available"
        else:
            return "Movie not found"
    except requests.RequestException as e:
        return f"Error: {e}"

# Append new movie poster links
for index in range(len(movie_poster_links), len(movie_titles)):
    poster_link = get_movie_poster(movie_titles[index])
    movie_poster_links.append(poster_link)
    print(poster_link)

# Save updated movie poster links
with open('exports/movie_posters.pkl', 'wb') as file:
    pickle.dump(movie_poster_links, file)

print(f"Total movie posters: {len(movie_poster_links)}")
