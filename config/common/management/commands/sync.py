import os
import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from data.product.models import Product  # Update with your actual app and model names


class Command(BaseCommand):
    help = "Fetch and save the first image from a product page based on product id."

    # You can define your cookies dictionary here
    cookies = {
        "_ym_uid": "1727868513689657695",
        "_ym_d": "1727868513",
        "was": "1",
        "PHPSESSID": "k0070f9lv6pm1a9aicsudkfo4m",
        "_csrf": 'cf2558f629121dbe586f41b1c226d06dc2e62e64321d3c941200cfd3ec58e7f1a:2:{i:0;s:5:"_csrf";i:1;s:32:"151J5S1CfPpYaKXwE442XhOI4zZp72lY";}',
    }

    def handle(self, *args, **kwargs):
        # Fetch products with categories only
        products = Product.objects.filter(
            category__isnull=False
        )  # Assuming `category` is a field on Product

        for product in products:
            product_id = product.iiko_id
            self.stdout.write(f"Fetching image for product id: {product_id}")

            # URL of the product page
            product_url = f"https://yummy.botagent.uz/groups/view-product?id={product_id}&region_id=1"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }

            # Make the request to the product page using the hardcoded cookies
            response = requests.get(product_url, headers=headers, cookies=self.cookies)
            if response.status_code == 200:
                # Parse the page content
                soup = BeautifulSoup(response.text, "html.parser")

                # Find the first image (adjust selector as needed)
                image_tag = soup.find("img")  # This will find the first image
                if image_tag:
                    image_url = image_tag.get("src")

                    if image_url:
                        self.download_and_save_image(product, image_url)
                    else:
                        self.stdout.write(
                            f"No image URL found for product id: {product_id}"
                        )
                else:
                    self.stdout.write(
                        f"No image tag found for product id: {product_id}"
                    )
            else:
                self.stdout.write(
                    f"Failed to fetch product page for id: {product_id}, status code: {response.status_code}"
                )

    def download_and_save_image(self, product: "Product", image_url: str):
        response = requests.get(image_url)
        if response.status_code == 200:
            file_name = os.path.basename(image_url)
            # Save the image to the product's image field (assuming it's an ImageField)
            product.image.save(file_name, ContentFile(response.content))
            product.save()
            self.stdout.write(f"Successfully saved image for product id: {product.id}")
        else:
            self.stdout.write(
                f"Failed to download image from {image_url}, status code: {response.status_code}"
            )
