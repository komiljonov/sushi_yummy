from io import BytesIO
import os
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from django.core.files import File as DjFile
from django.core.management.base import BaseCommand
from data.file.models import File
from data.product.models import Product  # Update with your actual app and model names


class Command(BaseCommand):
    help = "Fetch and save the first image from a product page based on product id and extract captions."

    cookies = {
        "_ym_uid": "1727868513689657695",
        "_ym_d": "1727868513",
        "was": "1",
        "PHPSESSID": "pkbptbgiojegs8ghoru0bdpet8",
        "_csrf": 'a1db76f52d9bf7c72a6c39cf4c83873e519270432fc6d147d2f63836513fe3eca%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22cotzfZf9jnm_P4FdjufUbuoAP28CPHjV%22%3B%7D',
    }

    def handle(self, *args, **kwargs):
        # Fetch products with categories only
        products = Product.objects.filter(category__isnull=False)

        for product in products:
            product_id = product.iiko_id
            self.stdout.write(
                f"Fetching image and captions for product id: {product_id}"
            )

            # URL of the product page
            product_url = f"https://yummy.botagent.uz/groups/view-product?id={product_id}&region_id=1"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }

            # Make the request to the product page using the hardcoded cookies
            response = requests.get(product_url, headers=headers, cookies=self.cookies)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                # Extract captions (Uzbek and Russian)
                caption_uz = self.extract_and_clean_caption(
                    soup, "#w0 > tr:nth-child(4) > td"
                )
                caption_ru = self.extract_and_clean_caption(
                    soup, "#w0 > tr:nth-child(2) > td"
                )

                self.stdout.write(f"Caption (UZ): {caption_uz}")
                self.stdout.write(f"Caption (RU): {caption_ru}")

                # Assign the captions to the product
                product.caption_uz = caption_uz
                product.caption_ru = caption_ru

                # Find the first image and save it
                image_tag = soup.find("img")
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

                # Save the product with updated captions and image
                product.save()
            else:
                self.stdout.write(
                    f"Failed to fetch product page for id: {product_id}, status code: {response.status_code}"
                )

    def extract_and_clean_caption(self, soup, css_selector):
        """Extracts caption from the given CSS selector and cleans the <br> tags."""
        element = soup.select_one(css_selector)
        if element:
            # Replace <br> with \n and remove HTML tags
            caption = element.get_text(separator="\n").strip()
            return caption
        return ""

    def download_and_save_image(self, product: "Product", image_url):
        # Check if the image URL is relative and if so, construct the full URL
        if image_url.startswith("/"):
            base_url = "https://yummy.botagent.uz"
            image_url = urljoin(base_url, image_url)

        # Proceed with downloading the image
        response = requests.get(image_url)
        if response.status_code == 200:
            file_name = os.path.basename(image_url)

            # Convert the image content to a BytesIO object
            image_content = BytesIO(response.content)

            new_file = File.objects.create(
                file=DjFile(image_content, file_name), filename=file_name
            )

            # Save the image to the product's image field using File
            product.image = new_file
            product.save()
            self.stdout.write(
                f"Successfully saved/updated image for product id: {product.id}"
            )
        else:
            self.stdout.write(
                f"Failed to download image from {image_url}, status code: {response.status_code}"
            )
