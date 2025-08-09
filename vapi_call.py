import requests
import json
from typing import Optional, Dict, Any


class VapiCaller:
    def __init__(self, private_api_key: str, assistant_id: str):
        """
        Initialize VapiCaller with API credentials

        Args:
            private_api_key: Your Vapi private API key
            assistant_id: Your Vapi assistant ID
        """
        self.base_url = "https://api.vapi.ai"
        self.private_api_key = private_api_key
        self.assistant_id = assistant_id
        self.headers = {
            "Authorization": f"Bearer {private_api_key}",
            "Content-Type": "application/json",
        }

    def make_call_with_variables(
        self,
        phone_number: str,
        variable_values: Dict[str, Any],
        customer_name: Optional[str] = None,
        call_name: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Make a call using Vapi API with custom variable values

        Args:
            phone_number: The phone number to call
            variable_values: Dictionary of variable values for template replacement
            customer_name: Name of the customer (optional)
            call_name: Name for the call (optional)
            **kwargs: Additional parameters to pass to the API

        Returns:
            API response as dictionary
        """
        # Prepare the request payload according to Vapi API documentation
        payload = {
            "assistantId": self.assistant_id,
            "phoneNumberId": "43ed3451-7453-4681-aa40-ab8754875a2d",
            "customer": {"number": f"+1{phone_number}"},  # Add +1 prefix for US numbers
            "type": "outboundPhoneCall",
            "assistantOverrides": {"variableValues": variable_values},
        }

        # Add optional parameters
        if call_name:
            payload["name"] = call_name

        # Add any additional parameters
        payload.update(kwargs)

        # Debug: print the payload being sent
        print(f"Debug - Payload being sent: {json.dumps(payload, indent=2)}")

        try:
            response = requests.post(
                f"{self.base_url}/call", headers=self.headers, json=payload
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {
                "error": True,
                "message": str(e),
                "status_code": (
                    getattr(e.response, "status_code", None)
                    if hasattr(e, "response")
                    else None
                ),
            }

    def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """
        Get the status of a call

        Args:
            call_id: The ID of the call to check

        Returns:
            Call status information
        """
        try:
            response = requests.get(
                f"{self.base_url}/call/{call_id}", headers=self.headers
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {
                "error": True,
                "message": str(e),
                "status_code": (
                    getattr(e.response, "status_code", None)
                    if hasattr(e, "response")
                    else None
                ),
            }
