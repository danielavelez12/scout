import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
import sys
import os

# Add the parent directory to the path to import spotify.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from spotify import SpotifyAPI
from vapi_call import VapiCaller

# Load environment variables
load_dotenv()


class SpotifyScout:
    """
    A scout class for fetching physics episodes from Spotify released today.
    """

    def __init__(self):
        """
        Initialize the SpotifyScout.
        """
        self.spotify_api = None
        self.results = []
        self.status = "idle"
        self.error_message = None
        self.subscribers = [{"name": "Daniela", "phone": "9549559235"}]

        # Spotify configuration from environment variables
        self.spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

        # Vapi configuration from environment variables
        self.vapi_private_api_key = os.getenv("PRIVATE_API_KEY")
        self.vapi_assistant_id = os.getenv("SPOTIFY_REPORTER_ASSISTANT_ID")
        self.vapi_phone_number_id = os.getenv("SPOTIFY_REPORTER_PHONE_NUMBER_ID")

    def _initialize_spotify(self):
        """
        Initialize Spotify API client.
        """
        try:
            if not self.spotify_client_id or not self.spotify_client_secret:
                raise ValueError(
                    "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables are required"
                )

            self.spotify_api = SpotifyAPI(
                self.spotify_client_id, self.spotify_client_secret
            )

        except Exception as e:
            self.error_message = f"Spotify initialization error: {str(e)}"
            self.status = "error"
            raise

    def fetch_physics_episodes(self) -> List[Dict[str, Any]]:
        """
        Fetch physics episodes from Spotify with release date filtering for past 7 days.

        Returns:
            List[Dict[str, Any]]: List of physics episode records from the past 7 days
        """
        try:
            self.status = "fetching"

            # Initialize Spotify API if not already done
            if self.spotify_api is None:
                print("Initializing Spotify API")
                self._initialize_spotify()

            # Calculate date range for past 7 days
            from datetime import datetime, timedelta

            today = datetime.now()
            sixty_days_ago = today - timedelta(days=60)
            print(f"Fetching episodes from {sixty_days_ago} to {today}")

            # Search for physics episodes with increased limit to get more results for filtering
            # Note: Spotify API doesn't support date filtering in search, so we'll filter by release_date after fetching
            search_results = self.spotify_api.search(
                "physics", search_type="episode", limit=50
            )
            print(f"Found {len(search_results['episodes']['items'])} episodes")

            if not search_results or "episodes" not in search_results:
                self.status = "completed"
                return []

            # Process and filter episodes by release date
            episodes = []
            for episode in search_results["episodes"]["items"]:
                release_date_str = episode.get("release_date", "")

                # Skip episodes without release date
                if not release_date_str:
                    continue

                # Parse release date and check if it's within the past 7 days
                try:
                    # Parse the release date (format: "YYYY-MM-DD")
                    release_date = datetime.strptime(release_date_str, "%Y-%m-%d")

                    # Only include episodes from the past 30 days
                    if release_date >= sixty_days_ago:
                        episode_record = {
                            "name": episode.get("name", ""),
                            "description": episode.get("description", ""),
                            "release_date": episode.get("release_date", ""),
                            "duration_ms": episode.get("duration_ms", 0),
                            "language": episode.get("language", ""),
                            "explicit": episode.get("explicit", False),
                            "audio_preview_url": episode.get("audio_preview_url", ""),
                            "images": episode.get("images", []),
                            "external_urls": episode.get("external_urls", {}),
                            "id": episode.get("id", ""),
                        }
                        episodes.append(episode_record)

                except ValueError:
                    # Skip episodes with invalid date formats
                    continue

            self.results = episodes
            self.status = "completed"
            return episodes

        except Exception as e:
            self.error_message = f"Fetch error: {str(e)}"
            self.status = "error"
            return []

    def check_spotify_config(self) -> bool:
        """
        Check if Spotify is properly configured with environment variables.

        Returns:
            bool: True if Spotify is configured, False otherwise
        """
        if not self.spotify_client_id:
            self.error_message = "SPOTIFY_CLIENT_ID environment variable not set"
            return False
        if not self.spotify_client_secret:
            self.error_message = "SPOTIFY_CLIENT_SECRET environment variable not set"
            return False
        return True

    def check_vapi_config(self) -> bool:
        """
        Check if Vapi is properly configured with environment variables.

        Returns:
            bool: True if Vapi is configured, False otherwise
        """
        if not self.vapi_private_api_key:
            self.error_message = "PRIVATE_API_KEY environment variable not set"
            return False
        if not self.vapi_assistant_id:
            self.error_message = "ASSISTANT_ID environment variable not set"
            return False
        if not self.vapi_phone_number_id:
            self.error_message = "PHONE_NUMBER_ID environment variable not set"
            return False
        return True

    def format_episodes_for_prompt(self, episodes: List[Dict[str, Any]]) -> str:
        """
        Format episodes data as a readable string for the Vapi prompt.

        Args:
            episodes: List of episode dictionaries

        Returns:
            str: Formatted episodes string for the prompt
        """
        if not episodes:
            return "No physics episodes released in the past week"

        formatted_episodes = []
        for episode in episodes:
            name = episode.get("name", "")
            release_date = episode.get("release_date", "")
            duration_ms = episode.get("duration_ms", 0)

            if name and release_date:
                # Format duration
                if duration_ms:
                    minutes = duration_ms // 1000 // 60
                    seconds = duration_ms // 1000 % 60
                    duration_str = f"{minutes}m {seconds}s"
                else:
                    duration_str = "Unknown duration"

                formatted_episodes.append(
                    f"{name} (Released: {release_date}, Duration: {duration_str})"
                )

        if formatted_episodes:
            return "\n".join(formatted_episodes)
        else:
            return "No physics episodes released in the past week"

    def report_results(self) -> bool:
        """
        Report physics episode results to all subscribers using Vapi calls.

        Returns:
            bool: True if reporting was successful, False otherwise
        """
        try:
            self.status = "reporting"

            if not self.check_vapi_config():
                print("Vapi not configured")
                self.status = "error"
                return False

            if not self.subscribers:
                self.error_message = "No subscribers to report to"
                self.status = "error"
                return False

            # Format episodes for the prompt
            episodes_text = self.format_episodes_for_prompt(self.results)
            print(f"Episodes to report: {episodes_text}")

            # Initialize Vapi caller
            vapi_caller = VapiCaller(
                self.vapi_private_api_key,
                self.vapi_assistant_id,
                self.vapi_phone_number_id,
            )

            # Report to each subscriber
            for subscriber in self.subscribers:
                subscriber_name = subscriber.get("name", "")
                subscriber_phone = subscriber.get("phone", "")

                if not subscriber_phone:
                    print(f"Warning: No phone number for subscriber {subscriber_name}")
                    continue

                # Prepare variable values for the call
                variable_values = {
                    "userFirstName": subscriber_name,
                    "recentPhysicsEpisodes": episodes_text,
                }

                print(
                    f"Calling {subscriber_name} at {subscriber_phone} about recent physics episodes"
                )

                # Make the call
                call_result = vapi_caller.make_call_with_variables(
                    phone_number=subscriber_phone,
                    variable_values=variable_values,
                )

                if call_result.get("error"):
                    print(
                        f"Error calling {subscriber_name}: {call_result.get('message')}"
                    )
                else:
                    print(
                        f"Successfully called {subscriber_name} about recent physics episodes"
                    )
                    print(f"Call ID: {call_result.get('id', 'N/A')}")

            self.status = "completed"
            return True

        except Exception as e:
            self.error_message = f"Report error: {str(e)}"
            self.status = "error"
            return False

    def format_episodes_for_display(self, episodes: List[Dict[str, Any]]) -> str:
        """
        Format episodes data as a readable string for display.

        Args:
            episodes: List of episode dictionaries

        Returns:
            str: Formatted episodes string
        """
        if not episodes:
            return "No physics episodes released in the past week"

        formatted_episodes = []
        for episode in episodes:
            name = episode.get("name", "Unknown Title")
            release_date = episode.get("release_date", "Unknown date")
            duration_ms = episode.get("duration_ms", 0)

            # Format duration
            if duration_ms:
                minutes = duration_ms // 1000 // 60
                seconds = duration_ms // 1000 % 60
                duration_str = f"{minutes}m {seconds}s"
            else:
                duration_str = "Unknown duration"

            formatted_episodes.append(
                f"{name} (Released: {release_date}, Duration: {duration_str})"
            )

        if formatted_episodes:
            return "\n".join(formatted_episodes)
        else:
            return "No physics episodes released today"


def main():
    """Main function to demonstrate SpotifyScout"""
    import argparse

    parser = argparse.ArgumentParser(
        description="SpotifyScout - Find and report physics episodes"
    )
    args = parser.parse_args()

    try:
        # Create scout instance
        scout = SpotifyScout()

        # Make Vapi calls to report results
        print("🔔 Making Vapi calls to report physics episodes...")
        success = scout.report_results()

        if not success:
            print(f"Error: {scout.error_message}")

    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
