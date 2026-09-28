import os
import django
import random
import requests
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.core.files.base import ContentFile
from product.models import Category

PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]

CATEGORY_KEYWORDS = {
    "Tech Accessories": "tech accessories",
    "Headphones and audio devices": "headphones",
    "Glasses and lighting": "sunglasses",
    "Watches and wearable accessories": "watch",
    "Personal Organization Tools and Supplies": "office stationery",
}


def fetch_photo_url(session, keyword):
    r = session.get(
        "https://api.pexels.com/v1/search",
        params={
            "query": keyword,
            "per_page": 30,
            "page": random.randint(1, 3),
            "orientation": "landscape",
        },
        timeout=20,
    )
    r.raise_for_status()
    photos = r.json().get("photos", [])
    if not photos:
        return None
    return random.choice(photos)["src"]["large"]


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
    categories = list(Category.objects.all())
    total = len(categories)
    print(f"Total categories: {total}\n")

    api = requests.Session()
    api.headers["Authorization"] = PEXELS_API_KEY
    cdn = requests.Session()

    done = 0

    for idx, category in enumerate(categories, start=1):
        print(f"[{idx}/{total}] {category.name}")

        if category.image:
            print("  • image already exists, skipping")
            continue

        keyword = CATEGORY_KEYWORDS.get(category.name, "product")

        try:
            url = fetch_photo_url(api, keyword)
        except requests.RequestException as e:
            print(f"  ✘ API error: {e}")
            continue

        if not url:
            print("  ✘ no photos found")
            continue

        content = download_image(cdn, url)
        if content:
            category.image.save(
                f"category_{category.id}.jpg",
                ContentFile(content),
                save=True,
            )
            done += 1
            print("  ✔ image added")
        else:
            print("  ✘ download failed")

        time.sleep(0.3)

    print("\n" + "=" * 40)
    print(f"Images added: {done}/{total}")
    print("=" * 40)


if __name__ == "__main__":
    main()