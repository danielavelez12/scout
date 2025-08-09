import requests
import base64
import json
from typing import Dict, Any, Optional


class SpotifyAPI:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.base_url = "https://api.spotify.com/v1"

    def get_access_token(self) -> str:
        """Get access token using Client Credentials flow"""
        if self.access_token:
            return self.access_token

        # Encode client credentials
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        # Request access token
        token_url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}

        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data["access_token"]
        return self.access_token

    def search(
        self, query: str, search_type: str = "episode", limit: int = 20
    ) -> Dict[str, Any]:
        """Search for items using the Spotify Search API"""
        print("Searching for episodes")
        token = self.get_access_token()

        headers = {"Authorization": f"Bearer {token}"}

        params = {"q": query, "type": search_type, "limit": limit}
        print(f"Params: {params}")

        response = requests.get(
            f"{self.base_url}/search", headers=headers, params=params
        )
        response.raise_for_status()

        return response.json()


def main():
    """Main function to demonstrate Spotify search"""
    # You'll need to set these environment variables or replace with your actual credentials
    import os
    from dotenv import load_dotenv

    load_dotenv()

    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        print(
            "❌ Error: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables are required."
        )
        print("Please set them in your .env file or environment.")
        print("\nTo get these credentials:")
        print("1. Go to https://developer.spotify.com/dashboard")
        print("2. Create a new app")
        print("3. Copy the Client ID and Client Secret")
        return

    try:
        # Initialize Spotify API
        spotify = SpotifyAPI(client_id, client_secret)

        # Search for "physics"
        print("🔍 Searching Spotify for 'physics' (episodes only)...")
        results = spotify.search("physics", search_type="episode", limit=10)

    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
