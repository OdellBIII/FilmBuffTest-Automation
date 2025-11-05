import os
import json
import requests
from typing import List, Dict, Optional


TMDB_API_KEY = os.getenv("GTA_TMDB_API_KEY")


class ActorMovieRecommender:
    """
    A client for fetching an actor's most popular movies using TMDB API.

    Note: TMDB API does not provide actual screen time data. This module uses
    cast order (billing position) as a proxy for screen time, since actors with
    more screen time typically have higher billing positions.
    """

    def __init__(self, api_key: str = TMDB_API_KEY):
        if not api_key:
            raise ValueError("TMDB API key must be provided")
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"

    def get_actor_top_movies(self, actor_name: str, limit: int = 9) -> str:
        """
        Fetches the top movies for a given actor, sorted by popularity and cast order.

        Args:
            actor_name: The name of the actor/actress to search for
            limit: Number of movies to return (default: 9)

        Returns:
            A JSON string containing the top movies with their details

        Raises:
            ValueError: If the actor is not found
            requests.RequestException: If there's an API error
        """
        # Step 1: Search for the actor to get their person_id
        person_id = self._search_actor(actor_name)

        # Step 2: Get the actor's movie credits
        movie_credits = self._get_movie_credits(person_id)

        # Step 3: Sort and filter movies
        top_movies = self._sort_and_filter_movies(movie_credits, limit)

        # Step 4: Return as JSON string
        result = {
            "actor_name": actor_name,
            "person_id": person_id,
            "total_movies_found": len(movie_credits),
            "movies": top_movies
        }

        return json.dumps(result, indent=2)

    def _search_actor(self, actor_name: str) -> int:
        """
        Search for an actor by name and return their person_id.

        Args:
            actor_name: The name of the actor to search for

        Returns:
            The TMDB person_id for the actor

        Raises:
            ValueError: If the actor is not found
        """
        search_url = f"{self.base_url}/search/person"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        params = {
            "query": actor_name,
            "include_adult": False,
            "language": "en-US",
            "page": 1
        }

        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            raise ValueError(f"Actor not found: {actor_name}")

        # Return the first (most popular) match
        actor = data["results"][0]
        return actor["id"]

    def _get_movie_credits(self, person_id: int) -> List[Dict]:
        """
        Get all movie credits for a given person.

        Args:
            person_id: The TMDB person_id

        Returns:
            A list of movie credit dictionaries
        """
        credits_url = f"{self.base_url}/person/{person_id}/movie_credits"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        params = {
            "language": "en-US"
        }

        response = requests.get(credits_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Return only the cast credits (not crew)
        return data.get("cast", [])

    def _sort_and_filter_movies(self, movie_credits: List[Dict], limit: int) -> List[Dict]:
        """
        Sort movies by popularity and cast order, then return the top N.

        The sorting algorithm prioritizes:
        1. Movies where the actor had a significant role (cast order <= 5)
        2. Within those, sort by popularity
        3. Finally, take the top N movies

        Args:
            movie_credits: List of movie credit dictionaries from TMDB
            limit: Number of movies to return

        Returns:
            A list of the top N movies with selected fields
        """
        # Filter out movies without required data
        valid_movies = [
            movie for movie in movie_credits
            if movie.get("popularity") and movie.get("order") is not None
        ]

        # Calculate a combined score:
        # - Lower order (better billing) is better
        # - Higher popularity is better
        # We'll weight popularity heavily and use order as a tiebreaker
        for movie in valid_movies:
            # Normalize order to a 0-1 scale (assuming max order of 50)
            # Lower order = higher score
            order_score = max(0, 1 - (movie.get("order", 50) / 50))

            # Combine: 80% popularity weight, 20% order weight
            popularity = movie.get("popularity", 0)
            movie["combined_score"] = (0.8 * popularity) + (0.2 * order_score * 100)

        # Sort by combined score (descending)
        sorted_movies = sorted(
            valid_movies,
            key=lambda x: x.get("combined_score", 0),
            reverse=True
        )

        # Take top N movies and extract relevant fields
        top_movies = []
        for movie in sorted_movies[:limit]:
            top_movies.append({
                "title": movie.get("title", "Unknown"),
                "release_year": movie.get("release_date", "")[:4] if movie.get("release_date") else None,
                "character": movie.get("character", ""),
                "cast_order": movie.get("order"),
                "popularity": movie.get("popularity"),
                "vote_average": movie.get("vote_average"),
                "movie_id": movie.get("id"),
                "overview": movie.get("overview", "")
            })

        return top_movies


def get_actor_movies_json(actor_name: str, api_key: Optional[str] = None) -> str:
    """
    Convenience function to get an actor's top 9 movies as JSON.

    Args:
        actor_name: The name of the actor/actress
        api_key: Optional TMDB API key (uses environment variable if not provided)

    Returns:
        A JSON string with the actor's top 9 movies

    Example:
        >>> json_result = get_actor_movies_json("Tom Hanks")
        >>> print(json_result)
    """
    recommender = ActorMovieRecommender(api_key=api_key or TMDB_API_KEY)
    return recommender.get_actor_top_movies(actor_name, limit=9)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ActorMovieRecommender.py 'Actor Name'")
        sys.exit(1)

    actor_name = " ".join(sys.argv[1:])

    try:
        result_json = get_actor_movies_json(actor_name)
        print(result_json)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except requests.RequestException as e:
        print(f"API Error: {e}")
        sys.exit(1)
