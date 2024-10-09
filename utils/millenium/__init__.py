# import urllib

from datetime import datetime, timedelta
import urllib.parse


try:
    import hashlib
    from time import sleep
    from urllib.parse import urlencode
    import httpx

    from bot.models import Location
    from data.taxi.models import Taxi
    from utils import after_minutes
    from data.cart.models import Cart
except Exception as e:
    print(e)


def after_minutes(minutes=20):

    # Get the current datetime and add 20 minutes
    new_time = datetime.now() + timedelta(minutes=minutes)

    # Format the datetime as 'YYYYMMDDHHMMSS'
    formatted_time = new_time.strftime("%Y%m%d%H%M%S")

    return formatted_time


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
        # query_string = self.get_query_string(data)
        query_string = urlencode(data)

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

        # Full URL with query parameters
        query_string = urlencode(data)

        # Generate the secret
        secret = self.getSecret(query_string)

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

        query_string = self.get_query_string(data)

        secret = self.getSecret(query_string)

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

    def analyze_route(self, loc1: "Location", loc2: "Location"):

        data = {
            "tariff_id": 47,
            "source_lat": loc1.latitude,
            "source_lon": loc1.longitude,
            "dest_lat": loc2.latitude,
            "dest_lon": loc2.longitude,
        }

        querystring = urlencode(data)

        secret = self.getSecret(querystring)

        full_url = f"{self.host}/analyze_route?{querystring}"

        response = self.client.get(
            full_url, headers={"Signature": secret, "X-User-Id": "10"}
        )

        data = response.json()["data"]

        return data

    def calc_order_cost(self, loc1: "Location", loc2: "Location"):

        analyze = self.analyze_route(loc1, loc2)

        data = {
            "tariff_id": 47,
            "is_prior": True,
            "source_time": after_minutes(),
            "distance_city": analyze["city_dist"],
            "source_zone_id": analyze["source_zone_id"],
            "dest_zone_id": analyze["dest_zone_id"],
        }

        querystring = urlencode(data)

        secret = self.getSecret(querystring)

        full_url = f"{self.host}/calc_order_cost?{querystring}"

        response = self.client.get(
            full_url, headers={"Signature": secret, "X-User-Id": "10"}
        )

        data = response.json()["data"]

        return data
