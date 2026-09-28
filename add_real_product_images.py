import os
import django
import random
import requests
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.core.files.base import ContentFile
from product.models import Product, ProductImage

PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]

CATEGORY_KEYWORDS = {
    "Tech Accessories": "tech gadget",
    "Headphones and audio devices": "headphones",
    "Glasses and lighting": "glasses",
    "Watches and wearable accessories": "watch",
    "Personal Organization Tools and Supplies": "desk office",
}


def fetch_photo_urls(session, keyword, count=4):
    r = session.get(
        "https://api.pexels.com/v1/search",
        params={
            "query": keyword,
            "per_page": 40,
            "page": random.randint(1, 5),
            "orientation": "square",
        },
        timeout=20,
    )
    r.raise_for_status()
    photos = r.json().get("photos", [])
    random.shuffle(photos)
    return [p["src"]["large"] for p in photos[:count]]


def download_image(session, url, retries=3):
    for attempt in range(1, retries + 1):
        try:
            r = session.get(url, timeout=20)
            ctype = r.headers.get("Content-Type", "")
            if r.status_code == 200 and ctype.startswith("image/") and len(r.content) > 1000:
                return r.content
            print(f"    attempt {attempt}: status={r.status_code}, type={ctype}")
        except requests.RequestException as e:
            print(f"    attempt {attempt}: {e}")
        time.sleep(attempt)
    return None


def main():
    products = list(
        Product.objects.select_related("category").prefetch_related("sub_images")
    )
    total = len(products)
    print(f"Total products: {total}\n")

    api = requests.Session()
    api.headers["Authorization"] = PEXELS_API_KEY
    cdn = requests.Session()

    main_done = sub_done = 0

    for idx, product in enumerate(products, start=1):
        print(f"[{idx}/{total}] {product.name}")

        category_name = product.category.name if product.category else ""
        keyword = CATEGORY_KEYWORDS.get(category_name, "product")

        need_main = not product.image
        need_subs = len(product.sub_images.all()) == 0
        if not (need_main or need_subs):
            print("  • already has images")
            continue

        sub_count = random.randint(1, 3) if need_subs else 0
        wanted = (1 if need_main else 0) + sub_count

        try:
            urls = fetch_photo_urls(api, keyword, wanted)
        except requests.RequestException as e:
            print(f"  ✘ API error: {e}")
            continue

        if need_main and urls:
            content = download_image(cdn, urls.pop(0))
            if content:
                product.image.save(f"product_{product.id}.jpg", ContentFile(content), save=True)
                main_done += 1
                print("  ✔ main image")
            else:
                print("  ✘ main failed")

        for j, url in enumerate(urls[:sub_count]):
            content = download_image(cdn, url)
            if content:
                ProductImage.objects.create(
                    product=product,
                    image=ContentFile(content, name=f"product_{product.id}_sub{j}.jpg"),
                )
                sub_done += 1
                print(f"  ✔ sub {j + 1}")

        time.sleep(0.3)

    print("\n" + "=" * 40)
    print(f"Main images added: {main_done}")
    print(f"Sub images added:  {sub_done}")
    print("=" * 40)


if __name__ == "__main__":
    main()