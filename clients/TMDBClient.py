import os
import requests


TMDB_API_KEY = os.getenv("GTA_TMDB_API_KEY")

class TMDBClient:
    def __init__(self, api_key=TMDB_API_KEY):
        if not api_key:
            raise ValueError("TMDB API key must be provided")
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/original"

    
    def download_actor_headshot(self, actor_name, save_path="headshot.jpg"):
        """
        Downloads the actor headshot for the given actor name using TMDB API.
        """
        # Check if headshot is already at saved path
        if os.path.exists(save_path):
            print(f"Headshot already exists at {save_path}")
            return save_path

        print(f"Searching for actor: {actor_name}")
        # Query TMDB for the actor
        search_url = f"{self.base_url}/search/person"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        params = {
            "query": actor_name
        }
        response = requests.get(search_url, headers=headers, params=params)
        data = response.json()

        if not data.get("results"):
            raise ValueError(f"Actor not found: {actor_name}")

        actor = data["results"][0]
        profile_path = actor.get("profile_path")
        if not profile_path:
            raise ValueError(f"No headshot available for {actor_name}")

        headshot_url = f"{self.image_base_url}{profile_path}"

        # Download the headshot image
        img_response = requests.get(headshot_url, stream=True)
        img_response.raise_for_status()

        with open(save_path, "wb") as f:
            for chunk in img_response.iter_content(1024):
                f.write(chunk)

        print(f"Headshot for '{actor_name}' saved as {save_path}")
        return save_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python TMDBClient.py 'Actor Name'")
        sys.exit(1)

    actor_name = " ".join(sys.argv[1:])
    filename = actor_name.replace(" ", "_") + ".jpg"
    client = TMDBClient()
    client.download_actor_headshot(actor_name, save_path=filename)