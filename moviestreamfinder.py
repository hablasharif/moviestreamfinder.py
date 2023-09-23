import streamlit as st
from imdb import IMDb
import pandas as pd
from tqdm import tqdm  # Import tqdm for the progress bar
import requests

# Streamlit App Title
st.title("Movie Search App")

# Sidebar
st.sidebar.header("Movie Details")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file with movie details", type=["csv"])

# Function to search for a movie and get IMDb URL
def search_movie_imdb(movie_name, release_year):
    ia = IMDb()
    movies = ia.search_movie(movie_name)

    # Filter movies by release year
    filtered_movies = [movie for movie in movies if "year" in movie and movie["year"] == release_year]

    if filtered_movies:
        movie = filtered_movies[0]  # Get the first matching movie
        imdb_id = movie.getID()
        imdb_url = f"https://www.imdb.com/title/tt{imdb_id}"
        return imdb_url
    else:
        return None

# Function to search for a movie and get TMDb ID
def search_movie_tmdb(movie_name, release_year):
    tmdb_api_key = "b0abe1120c53c9731ee3d32b81dd7df5"
    base_url = "https://api.themoviedb.org/3/search/movie"

    params = {
        "api_key": tmdb_api_key,
        "query": movie_name,
        "year": release_year
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            tmdb_id = data["results"][0]["id"]
            return tmdb_id
    return None

# Function to generate vidsrc URL with "tt" prefix
def generate_vidsrc_url(imdb_id=None, tmdb_id=None):
    if imdb_id:
        return f"https://vidsrc.to/embed/movie/tt{imdb_id}"
    elif tmdb_id:
        return f"https://vidsrc.to/embed/movie/{tmdb_id}"
    else:
        return None

# Function to get the title from a URL, using IMDb ID or TMDb ID as fallback
def get_title_from_url(vidsrc_url, imdb_id, tmdb_id):
    # Extract IMDb or TMDb ID from vidsrc URL
    if "tt" in vidsrc_url:
        imdb_id = vidsrc_url.split("tt")[-1]
    elif "tmdb" in vidsrc_url:
        tmdb_id = vidsrc_url.split("tmdb=")[-1]

    # Use IMDb or TMDb ID to fetch the title
    if imdb_id:
        ia = IMDb()
        movie = ia.get_movie(imdb_id)
        return movie.get("title")
    elif tmdb_id:
        tmdb_api_key = "b0abe1120c53c9731ee3d32b81dd7df5"
        base_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"

        params = {
            "api_key": tmdb_api_key,
        }

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            return data.get("original_title")
    return None

# Main content
if uploaded_file is not None:
    movie_data = pd.read_csv(uploaded_file)

    results = []

    # Use tqdm to create a progress bar
    progress_bar = st.progress(0)  # Initialize the progress bar
    with tqdm(total=len(movie_data)) as pbar:
        for index, row in movie_data.iterrows():
            movie_name = row['Movie Name']
            release_year = row['Release Year']

            imdb_url = search_movie_imdb(movie_name, release_year)
            tmdb_id = search_movie_tmdb(movie_name, release_year)

            # Generate the vidsrc URL
            vidsrc_url = generate_vidsrc_url(imdb_url, tmdb_id)
            
            # Get the title using IMDb ID or TMDb ID as fallback
            vidsrc_title = get_title_from_url(vidsrc_url, None, tmdb_id)

            results.append({
                'Movie Name': movie_name,
                'Release Year': release_year,
                'IMDb': imdb_url,
                'TMDb ID': tmdb_id,
                'vidsrc': vidsrc_url,
                'vidsrc_title': vidsrc_title
            })

            # Update the progress bar
            pbar.update(1)

            # Update the progress message in Streamlit
            st.text(f"Processed: {index + 1}/{len(movie_data)}")

    progress_bar.empty()  # Remove the progress bar after completion

    results_df = pd.DataFrame(results)

    st.subheader("Search Results")
    st.write(results_df)

    results_df.to_html("movie_search_results.html", index=False)
    results_df.to_excel("movie_search_results.xlsx", index=False)

    st.success("Search results saved to 'movie_search_results.html' and 'movie_search_results.xlsx'")

# Instructions
st.sidebar.header("Instructions")
st.sidebar.markdown(
    """
    1. Upload a CSV file with movie details containing columns 'Movie Name' and 'Release Year' in the sidebar.
    2. Click the 'Search' button to initiate the search.
    3. The app will display the search results and save them to HTML and Excel files.
    """
)
