import requests
import sys
import os
import re

# Get your free API key at http://www.omdbapi.com/apikey.aspx
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

class OMDBClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://www.omdbapi.com/"

    def extract_imdb_id(self, imdb_url):
        """
        Extracts the IMDB ID from an IMDB URL.

        Args:
            imdb_url (str): IMDB URL (e.g., https://www.imdb.com/title/tt0117500/)

        Returns:
            str: IMDB ID (e.g., tt0117500) or None if not found
        """
        if not imdb_url:
            return None

        # Match pattern like tt0117500 in the URL
        match = re.search(r'tt\d+', imdb_url)
        if match:
            return match.group(0)
        return None

    def download_movie_poster_by_imdb_id(self, imdb_id, save_path="poster.jpg"):
        """
        Downloads the movie poster for the given IMDB ID using OMDb API.

        Args:
            imdb_id (str): IMDB ID (e.g., tt0117500)
            save_path (str): Path where to save the poster

        Returns:
            str: Path to the saved poster file
        """
        # Check if poster is already at saved path
        if os.path.exists(save_path):
            print(f"Poster already exists at {save_path}")
            return save_path

        print(f"Searching for movie with IMDB ID: {imdb_id}")

        # Query OMDb for the movie using IMDB ID
        url = f"{self.base_url}?i={imdb_id}&apikey={self.api_key}"
        response = requests.get(url)
        data = response.json()

        if data.get("Response") == "False":
            raise ValueError(f"Movie not found with IMDB ID: {imdb_id}")

        poster_url = data.get("Poster")
        if not poster_url or poster_url == "N/A":
            raise ValueError(f"No poster available for IMDB ID: {imdb_id}")

        # Download the poster image
        img_response = requests.get(poster_url, stream=True)
        img_response.raise_for_status()

        with open(save_path, "wb") as f:
            for chunk in img_response.iter_content(1024):
                f.write(chunk)

        movie_title = data.get("Title", "Unknown")
        print(f"Poster for '{movie_title}' (IMDB ID: {imdb_id}) saved as {save_path}")
        return save_path

    def download_movie_poster(self, movie_title, save_path="poster.jpg", release_year=None, imdb_url=None):
        """
        Downloads the movie poster for the given movie title using OMDb API.
        If imdb_url is provided, it will use the IMDB ID instead of title/year.

        Args:
            movie_title (str): Title of the movie
            save_path (str): Path where to save the poster
            release_year (str): Optional release year to narrow search
            imdb_url (str): Optional IMDB URL to use for precise lookup

        Returns:
            str: Path to the saved poster file
        """
        # Check if poster is already at saved path
        if os.path.exists(save_path):
            print(f"Poster already exists at {save_path}")
            return save_path

        # If IMDB URL is provided, use that for lookup
        if imdb_url:
            imdb_id = self.extract_imdb_id(imdb_url)
            if imdb_id:
                return self.download_movie_poster_by_imdb_id(imdb_id, save_path)
            else:
                print(f"Warning: Could not extract IMDB ID from URL: {imdb_url}")
                if not movie_title:
                    raise ValueError(f"Could not extract IMDB ID from URL and no movie title provided: {imdb_url}")
                print("Falling back to title/year search")

        # Ensure we have a movie title for the search
        if not movie_title:
            raise ValueError("Either movie_title or a valid imdb_url must be provided")

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
    omdbClient = OMDBClient(OMDB_API_KEY)
    omdbClient.download_movie_poster(movie_title, save_path=filename)