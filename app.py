import streamlit as st
import pickle
import pandas as pd

# Load movie data & similarity matrix
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))  # <-- correct file name

# Function to fetch poster
def fetch_poster(poster_path):
    return "https://image.tmdb.org/t/p/w500" + poster_path

# Recommendation function
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movies = []
    recommended_posters = []

    for i in distances[1:6]:  # top 5
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movies.iloc[i[0]].poster_path))
    
    return recommended_movies, recommended_posters

# Streamlit UI
st.title("🎬 Movie Recommender System with Posters")

selected_movie = st.selectbox("Select a movie", movies['title'].values)

if st.button("Show Recommendations"):
    names, posters = recommend(selected_movie)
    for name, poster in zip(names, posters):
        st.subheader(name)
        st.image(poster)
