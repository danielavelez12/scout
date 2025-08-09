import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import sys
import requests
import json

# Add the parent directory to the path to import vapi_call
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vapi_call import VapiCaller

# Load environment variables
load_dotenv()


class GoogleFlightsScout:
    """
    A scout class for fetching flight deals under $500 to Europe from Fort Lauderdale (FLL).
    """

    def __init__(self):
        """
        Initialize the GoogleFlightsScout.
        """
        self.results = []
        self.status = "idle"
        self.error_message = None
        self.subscriber_phone = "9548023797"

        # SearchAPI configuration from environment variables
        self.search_api_key = os.getenv("SEARCH_API_KEY")

        # Vapi configuration from environment variables
        self.vapi_private_api_key = os.getenv("PRIVATE_API_KEY")
        self.vapi_assistant_id = os.getenv("FLIGHTS_REPORTER_ASSISTANT_ID")
        self.vapi_phone_number_id = os.getenv("FLIGHTS_REPORTER_PHONE_NUMBER_ID")

        # Flight search configuration
        self.departure_airport = "FLL"  # Fort Lauderdale
        self.max_price = 500
        self.search_months = 6  # Search for flights in the next 6 months

    def _get_european_airports(self) -> List[str]:
        """
        Get a list of major European airport codes for search.

        Returns:
            List[str]: List of European airport codes
        """
        return [
            "LHR",
            "CDG",
            "AMS",
            "FRA",
            "MAD",
            "BCN",
            "MXP",
            "FCO",
            "ZRH",
            "VIE",
            "BRU",
            "CPH",
            "ARN",
            "OSL",
            "HEL",
            "DUB",
            "EDI",
            "MAN",
            "LGW",
            "STN",
            "ORY",
            "NCE",
            "TLS",
            "BOD",
            "BER",
            "MUC",
            "DUS",
            "CGN",
            "HAM",
            "STR",
            "MIL",
            "NAP",
            "BRI",
            "BGO",
            "TRD",
            "GOT",
            "MAL",
            "VLC",
            "BIL",
            "SVQ",
        ]

    def _search_flights_to_airport(
        self, arrival_airport: str, outbound_date: str
    ) -> List[Dict[str, Any]]:
        """
        Search for flights to a specific European airport.

        Args:
            arrival_airport: Destination airport code
            outbound_date: Departure date in YYYY-MM-DD format

        Returns:
            List[Dict[str, Any]]: List of flight options
        """
        try:
            url = "https://www.searchapi.io/api/v1/search"

            params = {
                "engine": "google_flights",
                "flight_type": "round_trip",
                "departure_id": self.departure_airport,
                "arrival_id": arrival_airport,
                "outbound_date": outbound_date,
                "return_date": self._get_return_date(outbound_date),
                "gl": "us",
                "hl": "en",
            }

            headers = {"Authorization": f"Bearer {self.search_api_key}"}

            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()

            # Extract flight options
            flight_options = []
            if "flight_options" in data:
                for option in data["flight_options"]:
                    price = option.get("price", 0)

                    # Only include flights under $500
                    if price <= self.max_price:
                        flight_info = {
                            "departure_airport": self.departure_airport,
                            "arrival_airport": arrival_airport,
                            "outbound_date": outbound_date,
                            "return_date": self._get_return_date(outbound_date),
                            "price": price,
                            "airline": option.get("book_with", "Unknown"),
                            "flight_numbers": option.get("flight_numbers", []),
                            "duration": option.get("duration", "Unknown"),
                            "stops": option.get("stops", "Unknown"),
                        }
                        flight_options.append(flight_info)

            return flight_options

        except Exception as e:
            print(f"Error searching flights to {arrival_airport}: {str(e)}")
            return []

    def _get_return_date(self, outbound_date: str) -> str:
        """
        Calculate return date (7 days after outbound).

        Args:
            outbound_date: Outbound date in YYYY-MM-DD format

        Returns:
            str: Return date in YYYY-MM-DD format
        """
        outbound = datetime.strptime(outbound_date, "%Y-%m-%d")
        return_date = outbound + timedelta(days=7)
        return return_date.strftime("%Y-%m-%d")

    def _get_search_dates(self) -> List[str]:
        """
        Generate search dates for the next 6 months.

        Returns:
            List[str]: List of dates in YYYY-MM-DD format
        """
        dates = []
        today = datetime.now()

        for i in range(self.search_months):
            # Start from next month to avoid same-day bookings
            search_date = today + timedelta(days=30 + (i * 30))
            dates.append(search_date.strftime("%Y-%m-%d"))

        return dates

    def fetch_flight_deals(self) -> List[Dict[str, Any]]:
        """
        Fetch flight deals under $500 to Europe from Fort Lauderdale.

        Returns:
            List[Dict[str, Any]]: List of flight deals
        """
        try:
            self.status = "fetching"

            if not self.check_search_api_config():
                self.status = "error"
                return []

            print(
                f"Searching for flights under ${self.max_price} to Europe from {self.departure_airport}"
            )

            european_airports = self._get_european_airports()
            search_dates = self._get_search_dates()

            all_flights = []

            # Search for flights to each European airport
            for airport in european_airports:
                print(f"Searching flights to {airport}...")

                for date in search_dates:
                    flights = self._search_flights_to_airport(airport, date)
                    all_flights.extend(flights)

                    # Add a small delay to avoid rate limiting
                    import time

                    time.sleep(0.5)

            # Sort by price (lowest first)
            all_flights.sort(key=lambda x: x.get("price", 0))

            # Limit to top 20 deals
            self.results = all_flights[:20]

            print(f"Found {len(self.results)} flight deals under ${self.max_price}")

            self.status = "completed"
            return self.results

        except Exception as e:
            self.error_message = f"Fetch error: {str(e)}"
            self.status = "error"
            return []

    def check_search_api_config(self) -> bool:
        """
        Check if SearchAPI is properly configured with environment variables.

        Returns:
            bool: True if SearchAPI is configured, False otherwise
        """
        if not self.search_api_key:
            self.error_message = "SEARCH_API_KEY environment variable not set"
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
            self.error_message = (
                "FLIGHTS_REPORTER_ASSISTANT_ID environment variable not set"
            )
            return False
        if not self.vapi_phone_number_id:
            self.error_message = (
                "FLIGHTS_REPORTER_PHONE_NUMBER_ID environment variable not set"
            )
            return False
        return True

    def format_flights_for_prompt(self, flights: List[Dict[str, Any]]) -> str:
        """
        Format flights data as a readable string for the Vapi prompt.

        Args:
            flights: List of flight dictionaries

        Returns:
            str: Formatted flights string for the prompt
        """
        if not flights:
            return f"No flight deals found under ${self.max_price} to Europe from {self.departure_airport}"

        formatted_flights = []
        for flight in flights:
            departure = flight.get("departure_airport", "")
            arrival = flight.get("arrival_airport", "")
            outbound_date = flight.get("outbound_date", "")
            return_date = flight.get("return_date", "")
            price = flight.get("price", 0)
            airline = flight.get("airline", "Unknown")

            if departure and arrival and outbound_date:
                formatted_flights.append(
                    f"{departure} to {arrival} (${price}) - {airline} - Out: {outbound_date}, Return: {return_date}"
                )

        if formatted_flights:
            return (
                f"Found {len(formatted_flights)} flight deals under ${self.max_price}:\n"
                + "\n".join(formatted_flights)
            )
        else:
            return f"No flight deals found under ${self.max_price} to Europe from {self.departure_airport}"

    def report_results(self) -> bool:
        """
        Report flight deals to the subscriber using Vapi call.

        Returns:
            bool: True if reporting was successful, False otherwise
        """
        try:
            self.status = "reporting"

            if not self.check_vapi_config():
                print("Vapi not configured")
                self.status = "error"
                return False

            if not self.subscriber_phone:
                self.error_message = "No subscriber phone number to report to"
                self.status = "error"
                return False

            # Format flights for the prompt
            flights_text = self.format_flights_for_prompt(self.results)
            print(f"Flights to report: {flights_text}")

            # Initialize Vapi caller
            vapi_caller = VapiCaller(
                self.vapi_private_api_key,
                self.vapi_assistant_id,
                self.vapi_phone_number_id,
            )

            # Prepare variable values for the call
            variable_values = {
                "userFirstName": "Daniela",
                "flightDeals": flights_text,
            }

            print(f"Calling {self.subscriber_phone} about flight deals to Europe")

            # Make the call
            call_result = vapi_caller.make_call_with_variables(
                phone_number=self.subscriber_phone,
                variable_values=variable_values,
            )

            if call_result.get("error"):
                print(f"Error calling subscriber: {call_result.get('message')}")
                self.status = "error"
                return False
            else:
                print(f"Successfully called subscriber about flight deals")
                print(f"Call ID: {call_result.get('id', 'N/A')}")

            self.status = "completed"
            return True

        except Exception as e:
            self.error_message = f"Report error: {str(e)}"
            self.status = "error"
            return False

    def format_flights_for_display(self, flights: List[Dict[str, Any]]) -> str:
        """
        Format flights data as a readable string for display.

        Args:
            flights: List of flight dictionaries

        Returns:
            str: Formatted flights string
        """
        if not flights:
            return f"No flight deals found under ${self.max_price} to Europe from {self.departure_airport}"

        formatted_flights = []
        for flight in flights:
            departure = flight.get("departure_airport", "Unknown")
            arrival = flight.get("arrival_airport", "Unknown")
            outbound_date = flight.get("outbound_date", "Unknown date")
            return_date = flight.get("return_date", "Unknown date")
            price = flight.get("price", 0)
            airline = flight.get("airline", "Unknown airline")

            formatted_flights.append(
                f"{departure} → {arrival} | ${price} | {airline} | {outbound_date} - {return_date}"
            )

        if formatted_flights:
            return (
                f"Found {len(formatted_flights)} flight deals under ${self.max_price}:\n"
                + "\n".join(formatted_flights)
            )
        else:
            return f"No flight deals found under ${self.max_price} to Europe from {self.departure_airport}"


def main():
    """Main function to demonstrate GoogleFlightsScout"""
    import argparse

    parser = argparse.ArgumentParser(
        description="GoogleFlightsScout - Find and report flight deals to Europe"
    )
    args = parser.parse_args()

    try:
        # Create scout instance
        scout = GoogleFlightsScout()

        # Fetch flight deals
        print("✈️ Fetching flight deals to Europe...")
        flights = scout.fetch_flight_deals()

        if flights:
            print(f"Found {len(flights)} flight deals!")
            print(scout.format_flights_for_display(flights))
        else:
            print("No flight deals found.")

        # Make Vapi call to report results
        print("🔔 Making Vapi call to report flight deals...")
        success = scout.report_results()

        if not success:
            print(f"Error: {scout.error_message}")

    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
