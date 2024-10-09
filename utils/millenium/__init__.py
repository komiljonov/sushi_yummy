# import urllib
from data.cart.models import Cart

import urllib.parse


try:
    import hashlib
    from time import sleep
    from urllib.parse import urlencode
    import httpx

    from bot.models import Location
    from data.taxi.models import Taxi
    from utils import after_minutes
except Exception as e:
    print(e)


class Millenium:

    host: str = "https://millennium.tm.taxi:8089/common_api/1.0"

    def __init__(self, token: str):
        self.token = token
        self.client = httpx.Client(verify=False)  # Disabling SSL verification

    def md5(self, string: str) -> str:
        """Helper method to calculate MD5 hash."""
        return hashlib.md5(string.encode()).hexdigest()

    def getSecret(self, data: str) -> str:
        """Generates a secret based on the data and the token."""
        # Create a string from the data dictionary (concatenate key-value pairs)
        # data_string = "".join(
        #     f"{key}={str(value)}&" for key, value in data.items()
        # ).rstrip("&")

        data_string = data

        print(data_string)

        # Combine the data string with the token
        string_to_hash = data_string + self.token

        # Return the MD5 hash of the combined string
        return self.md5(string_to_hash)

    # def get_query_string(self, data: dict):
    #     return "&".join(f"{key}={value}" for key, value in data.items())

    def get_query_string(self, data: dict):
        return "&".join(
            f"{key}={urllib.parse.quote_plus(str(value))}"
            for key, value in data.items()
        )

    def _create_order(self, cart: "Cart"):
        """Constructs the URL for creating an order, sends the request, and returns the response."""

        data = {
            "tariff_id": 47,
            "phone": cart.phone_number.replace("+", ""),
            "source": 1,
            "customer": 10,
            "is_prior": "true",
            "source_lat": cart.filial.location.latitude,
            "source_lon": cart.filial.location.longitude,
            "dest_lat": cart.location.latitude,
            "dest_lon": cart.location.longitude,
            "source_time": after_minutes(20),
            "comment": (
                f"Sushi Yummy\n\n"
                f"Buyurtma raqami: {cart.order_id}\n"
                f"To'lov turi: {cart.payment.provider}\n"
                f"Buyurtma narxi: {cart.price}\n"
            ),
        }

        # Manually build the query string using a for loop
        # query_string = "&".join(f"{key}={value}" for key, value in data.items())
        query_string = self.get_query_string(data)

        # Generate the secret
        secret = self.getSecret(query_string)

        # Full URL
        full_url = f"{self.host}/create_order?{query_string}"
        print(full_url)

        # Send the POST request using the httpx client with SSL verification disabled
        response = self.client.post(
            full_url, headers={"Signature": secret, "X-User-Id": "10"}
        )

        print(response.text)

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

    def create_order(self, cart: "Cart"):

        order = self._create_order(cart)

        if order.status_code != 200:
            return None

        order_data = order.json()

        sleep(5)

        state = self.get_order_state(order_data["data"]["order_id"])
        # state = self.get_order_state(1168813)

        data: dict = state.json()["data"]

        driver_data = self.get_driver_info(data["driver_id"])

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
            driver_phone_number=driver_data.get("phone_number"),
        )

        return new_taxi

    def get_driver_info(self, driver_id: int):

        data = {"driver_id": driver_id}

        secret = self.getSecret(data)

        query_string = self.get_query_string(data)

        full_url = f"{self.host}/get_driver_info?{query_string}"

        response = self.client.get(
            full_url, headers={"Signature": secret, "X-User-Id": "10"}
        )

        data = response.json()["data"]

        return {
            "name": data.get("name"),
            "balance": data.get("balance"),
            "phone_number": data.get("mobile_phone"),
            "passport": data.get("passport"),
        }


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
