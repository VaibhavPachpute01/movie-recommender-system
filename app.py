import streamlit as st
import pickle
import pandas as pd
import requests
import time
import os
import gdown  # ✅ important

# -------------------------------
# 🔽 Download similarity.pkl using gdown
# -------------------------------
FILE_ID = "1IG-oBU25CIJkuOKVjfxgkqUgKeUC9qLR"
FILE_NAME = "similarity.pkl"

if not os.path.exists(FILE_NAME):
    url = f"https://drive.google.com/uc?id={FILE_ID}"
    gdown.download(url, FILE_NAME, quiet=False)

# -------------------------------
# 🔽 Safety check
# -------------------------------
if not os.path.exists(FILE_NAME) or os.path.getsize(FILE_NAME) < 1000000:
    st.error("❌ similarity.pkl not downloaded properly.")
    st.stop()

# -------------------------------
# 🔽 Load Data
# -------------------------------
movies_df = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# -------------------------------
# 🔽 UI
# -------------------------------
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    "Select a movie to get recommendations:",
    movies_df['title'].values
)

# -------------------------------
# 🔽 Fetch Poster
# -------------------------------
def fetch_poster(movie_id):
    api_key = os.getenv("TMDB_API_KEY")

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
    index = movies_df[movies_df['title'] == movie].index[0]
    distances = similarity[index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    names = []
    posters = []

    for i in movies_list:
        movie_id = movies_df.iloc[i[0]].id
        names.append(movies_df.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))
        time.sleep(0.2)

    return names, posters

# -------------------------------
# 🔽 Button
# -------------------------------
if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])
