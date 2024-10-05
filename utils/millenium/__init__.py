from dataclasses import dataclass
import hashlib
from time import sleep
from urllib.parse import urlencode
import httpx

from bot.models import Location
from data.taxi.models import Taxi


class Millenium:

    host: str = "https://millennium.tm.taxi:8089/common_api/1.0"

    def __init__(self, token: str):
        self.token = token
        self.client = httpx.Client(verify=False)  # Disabling SSL verification

    def md5(self, string: str) -> str:
        """Helper method to calculate MD5 hash."""
        return hashlib.md5(string.encode()).hexdigest()

    def getSecret(self, data: dict) -> str:
        """Generates a secret based on the data and the token."""
        # Create a string from the data dictionary (concatenate key-value pairs)
        data_string = "".join(
            f"{key}={str(value)}&" for key, value in data.items()
        ).rstrip("&")

        # Combine the data string with the token
        string_to_hash = data_string + self.token

        # Return the MD5 hash of the combined string
        return self.md5(string_to_hash)

    def _create_order(self, phone: str, filial: Location, clientaddress: Location):
        """Constructs the URL for creating an order, sends the request, and returns the response."""

        # Data to be included in the URL and for the secret generation
        data = {
            "phone": phone,
            "source": 1,
            "source_lat": filial.latitude,
            "source_lon": filial.longitude,
            "dest_lat": clientaddress.latitude,
            "dest_lon": clientaddress.longitude,
            "source_time": "20240926200351",  # Example time format
            "customer": "10",
            "comment": "Salom",  # Change comment as needed
            "crew_group_id": "27",
        }

        # Generate the secret
        secret = self.getSecret(data)

        # Generate the query string using the data
        query_string = urlencode(data)

        # Full URL
        full_url = f"{self.host}/create_order?{query_string}"
        print(full_url)

        # Send the POST request using the httpx client with SSL verification disabled
        response = self.client.post(
            full_url, headers={"Signature": secret, "X-User-Id": "10"}
        )

        # Return the response object (or response text)
        return response

    def get_order_state(self, order_id: str):
        """Retrieves the state of a specific order using its order ID."""

        # Data to include in the URL
        data = {"order_id": order_id}

        # Generate the secret
        secret = self.getSecret(data)

        # Full URL with query parameters
        query_string = urlencode(data)
        full_url = f"{self.host}/get_order_state?{query_string}"
        print(full_url)

        # Send the GET request with SSL verification disabled
        response = self.client.get(
            full_url, headers={"Signature": secret, "X-User-Id": "10"}
        )

        # Return the response object (or response text)
        return response

    def create_order(self, phone: str, filial: Location, clientaddress: Location):

        order = self._create_order(phone, filial, clientaddress)

        if order.status_code != 200:
            return None

        order_data = order.json()
        state = self.get_order_state(order_data["data"]["order_id"])

        data: dict = state.json()["data"]

        new_taxi = Taxi.objects.create(
            order_id=data["order_id"],
            state_id=data["state_id"],
            state_kind=data["state_kind"],
            crew_id=data.get("crew_id"),
            car_id=data.get("car_id"),
            start_time=int(data["start_time"]) if data.get("start_time") else None,
            sourcetime=int(data["source_time"]) if data.get("source_time") else None,
            source_lat=data.get("source_lat"),
            source_lon=data.get("source_lon"),
            destination_lat=data.get("destination_lat"),
            destination_lon=data.get("destination_lon"),
            phone=data.get("phone"),
            client_id=data.get("client_id"),
            sum=data.get("sum"),
            total_sum=data.get("total_sum"),
            car_mark=data.get("car_mark"),
            car_model=data.get("car_model"),
            car_color=data.get("car_color"),
            car_number=data.get("car_number"),
            driver_phone_number=data.get("phone_to_dial"),
        )
        return new_taxi


# # Example usage
# millenium = Millenium(token="3E8EA3F2-4776-4E1C-9A97-E4C13C5AEF1C")

# # Sample locations for filial and client address
# filial = Location(latitude=41.2714904, longitude=69.2316963)
# clientaddress = Location(latitude=41.312343, longitude=69.1645997)

# # Call the create_order method
# order = millenium._create_order(
#     phone="998909755211", filial=filial, clientaddress=clientaddress
# )


# # Output the response content
# print("Response Status Code:", order.status_code)
# print("Response Text:", order.text)


# sleep(3)
# state = millenium.get_order_state(order.json()["data"]["order_id"])
# # state = millenium.get_order_state(1168813)


# print(state.text)
