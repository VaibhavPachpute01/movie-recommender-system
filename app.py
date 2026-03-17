import streamlit as st
import pickle
import pandas as pd
import requests
import time
import os

# -------------------------------
# 🔽 Function to download file from Google Drive
# -------------------------------
def download_file_from_google_drive(file_id, destination):
    URL = "https://drive.google.com/uc?export=download"
    
    session = requests.Session()
    response = session.get(URL, params={'id': file_id}, stream=True)

    # Handle large file warning
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            params = {'id': file_id, 'confirm': value}
            response = session.get(URL, params=params, stream=True)
            break

    with open(destination, "wb") as f:
        for chunk in response.iter_content(32768):
            if chunk:
                f.write(chunk)

# -------------------------------
# 🔽 Download similarity.pkl (ONLY if not exists)
# -------------------------------
file_id = "1IG-oBU25CIJkuOKVjfxgkqUgKeUC9qLR"

if not os.path.exists("similarity.pkl"):
    download_file_from_google_drive(file_id, "similarity.pkl")

# -------------------------------
# 🔽 Safety check (prevent corruption)
# -------------------------------
if os.path.getsize("similarity.pkl") < 1000000:
    st.error("❌ similarity.pkl not downloaded correctly. Please check file access.")
    st.stop()

# -------------------------------
# 🔽 Load Data
# -------------------------------
movies_df = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# -------------------------------
# 🔽 Streamlit UI
# -------------------------------
st.title('🎬 Movie Recommender System')

movie_titles = movies_df['title'].values
selected_movie_name = st.selectbox(
    "Select a movie to get recommendations:",
    movie_titles
)

# -------------------------------
# 🔽 Fetch Poster from TMDB
# -------------------------------
def fetch_poster(movie_id):
    api_key = os.getenv("TMDB_API_KEY")  # ✅ secure

    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return "https://via.placeholder.com/500x750?text=No+Image"

        data = response.json()
        poster_path = data.get('poster_path')

        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"

    except:
        return "https://via.placeholder.com/500x750?text=Error"

# -------------------------------
# 🔽 Recommendation Logic
# -------------------------------
def recommend(movie):
    movie_index = movies_df[movies_df['title'] == movie].index[0]
    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_movies_poster = []

    for i in movie_list:
        movie_id = movies_df.iloc[i[0]].id
        recommended_movies.append(movies_df.iloc[i[0]].title)
        recommended_movies_poster.append(fetch_poster(movie_id))
        time.sleep(0.2)  # ✅ avoid API blocking

    return recommended_movies, recommended_movies_poster

# -------------------------------
# 🔽 Button Action
# -------------------------------
if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])
