import requests
import sys
import os

# Get your free API key at http://www.omdbapi.com/apikey.aspx
OMDB_API_KEY = "your_api_key_here"

class OMDBClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://www.omdbapi.com/"

    def download_movie_poster(self, movie_title, save_path="poster.jpg", release_year=None):
        """
        Downloads the movie poster for the given movie title using OMDb API.
        """
        # Check if poster is already at saved path
        if os.path.exists(save_path):
            print(f"Poster already exists at {save_path}")
            return save_path
        print(f"Searching for movie: {movie_title}")
        # Query OMDb for the movie
        url = f"{self.base_url}?t={movie_title}&apikey={self.api_key}"
        if release_year:
            url += f"&y={release_year}"
        response = requests.get(url)
        data = response.json()

        if data.get("Response") == "False":
            raise ValueError(f"Movie not found: {movie_title}")

        poster_url = data.get("Poster")
        if not poster_url or poster_url == "N/A":
            raise ValueError(f"No poster available for {movie_title}")

        # Download the poster image
        img_response = requests.get(poster_url, stream=True)
        img_response.raise_for_status()

        with open(save_path, "wb") as f:
            for chunk in img_response.iter_content(1024):
                f.write(chunk)

        print(f"Poster for '{movie_title}' saved as {save_path}")
        return save_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_poster.py 'Movie Title'")
        sys.exit(1)

    movie_title = " ".join(sys.argv[1:])
    filename = movie_title.replace(" ", "_") + ".jpg"
    download_movie_poster(movie_title, save_path=filename)