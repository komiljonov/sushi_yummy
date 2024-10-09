import requests


def reverse_geocode(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"

    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "addressdetails": 1,
    }

    headers = {
        "User-Agent": "SushiYummy/1.0 (komiljonovshukurullokh@gmail.com)"  # Replace with your app's name and email
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data: dict = response.json()

        print(data)

        address: dict = data.get("address", {})

        # Extract relevant parts of the address
        office = address.get("office", "")
        house_number = address.get("house_number", "")
        county = address.get("county", "")
        road = address.get("road", "")
        neighbourhood = address.get("neighbourhood", "")
        city = address.get("city", "")
        country = address.get("country", "")

        # Format the address in a meaningful way
        meaningful_address = ", ".join(
            part
            for part in [
                office,
                house_number,
                road,
                neighbourhood,
                county,
                city,
                country,
            ]
            if part
        )

        return meaningful_address or data.get("display_name")
    else:
        return None
