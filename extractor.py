# import re
# import json
# import os
# import time
# import requests  # type: ignore
# from requests.exceptions import RequestException, Timeout  # type: ignore
# from dotenv import load_dotenv

# # ───────────────── CONFIG ─────────────────
# OUTPUT_DIR = "output"
# UPLOAD_TO_STRAPI = True  # 🔥 set True when you want uploads

# load_dotenv()

# STRAPI_URL = os.getenv("STRAPI_URL")
# STRAPI_TOKEN = os.getenv("STRAPI_TOKEN")

# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # ───────────────── ERRORS ─────────────────
# class SteamExtractorError(Exception):
#     """Custom exception for Steam extractor errors"""
#     pass


# # ───────────────── HELPERS ─────────────────
# def extract_app_id(url: str) -> str:
#     if not isinstance(url, str) or not url.strip():
#         raise SteamExtractorError("URL is empty or not a string")

#     match = re.search(r"/app/(\d+)", url)
#     if not match:
#         raise SteamExtractorError("Invalid Steam product URL")

#     return match.group(1)


# def fetch_steam_data(app_id: str) -> dict:
#     api_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"

#     try:
#         response = requests.get(api_url, timeout=10)
#         response.raise_for_status()
#     except Timeout:
#         raise SteamExtractorError("Steam API request timed out")
#     except RequestException as e:
#         raise SteamExtractorError(f"Network error: {e}")

#     try:
#         data = response.json()
#     except ValueError:
#         raise SteamExtractorError("Invalid JSON received from Steam")

#     if app_id not in data or not data[app_id].get("success"):
#         raise SteamExtractorError("Steam API returned success=false")

#     return data[app_id]["data"]


# def build_payload(app_id: str, url: str, game: dict) -> dict:
#     screenshots = [
#         s.get("path_full")
#         for s in game.get("screenshots", [])
#         if s.get("path_full")
#     ]

#     return {
#         "app_id": app_id,
#         "name": game.get("name", "Unknown"),
#         "source": url,
#         "images": {
#             "header": game.get("header_image"),
#             "screenshots": screenshots,
#         },
#     }


# def save_json(app_id: str, payload: dict) -> None:
#     file_path = os.path.join(OUTPUT_DIR, f"app_{app_id}.json")
#     try:
#         with open(file_path, "w", encoding="utf-8") as f:
#             json.dump(payload, f, indent=2)
#         print(f"✅ Saved → {file_path}")
#     except OSError as e:
#         raise SteamExtractorError(f"Failed to write JSON file: {e}")


# # ───────────────── STRAPI UPLOADER ─────────────────
# def upload_image_to_strapi(image_url: str) -> bool:
#     if not STRAPI_URL or not STRAPI_TOKEN:
#         print("⚠️ STRAPI env not set, skipping upload")
#         return False

#     try:
#         img_res = requests.get(image_url, timeout=20)
#         img_res.raise_for_status()

#         filename = image_url.split("?")[0].split("/")[-1]

#         files = [
#             (
#                 "files",
#                 (
#                     filename,
#                     img_res.content,
#                     img_res.headers.get("Content-Type") or "image/jpeg",
#                 ),
#             )
#         ]

#         res = requests.post(
#             f"{STRAPI_URL}/api/upload",
#             headers={
#                 "Authorization": f"Bearer {STRAPI_TOKEN}",
#             },
#             files=files,
#             timeout=30,
#         )

#         if res.status_code != 200:
#             print("✅ Upload response:", res.text)
#             res.raise_for_status()

#         return True

#     except RequestException as e:
#         print(f"❌ Upload failed: {image_url}")
#         print(f"   Reason: {e}")
#         return False



# def upload_images(payload: dict) -> None:
#     images = []
#     if payload["images"]["header"]:
#         images.append(payload["images"]["header"])
#     images.extend(payload["images"]["screenshots"])

#     success, failed = 0, 0

#     for img in images:
#         if upload_image_to_strapi(img):
#             success += 1
#         else:
#             failed += 1
#         time.sleep(0.5)

#     print(f"⬆️ Uploaded: {success} | Failed: {failed}")


# # ───────────────── MAIN FLOW ─────────────────
# def process_url(url: str) -> None:
#     print(f"\n🔍 Processing: {url}")

#     try:
#         app_id = extract_app_id(url)
#         game_data = fetch_steam_data(app_id)
#         payload = build_payload(app_id, url, game_data)
#         save_json(app_id, payload)

#         image_count = (
#             1 if payload["images"]["header"] else 0
#         ) + len(payload["images"]["screenshots"])

#         print(f"🖼️ Extracted {image_count} image URLs")

#         if UPLOAD_TO_STRAPI:
#             upload_images(payload)

#     except SteamExtractorError as e:
#         print(f"❌ Error: {e}")
#     except Exception as e:
#         print(f"🔥 Unexpected error: {e}")


# def load_urls(file_path: str) -> list:
#     if not os.path.exists(file_path):
#         raise SteamExtractorError(f"Input file not found: {file_path}")

#     with open(file_path, "r", encoding="utf-8") as f:
#         return [line.strip() for line in f if line.strip()]


# if __name__ == "__main__":
#     try:
#         urls = load_urls("steam_links.txt")
#     except SteamExtractorError as e:
#         print(f"❌ Startup error: {e}")
#         exit(1)

#     for url in urls:
#         process_url(url)

#     print("\n🎉 Finished processing all URLs.")





import re
import json
import os
import time
import requests
from requests.exceptions import RequestException, Timeout
from dotenv import load_dotenv

# ───────────────── CONFIG ─────────────────
OUTPUT_DIR = "output"
UPLOAD_TO_STRAPI = False  # 🔥 set True when you want uploads

load_dotenv()

STRAPI_URL = os.getenv("STRAPI_URL")
STRAPI_TOKEN = os.getenv("STRAPI_TOKEN")

os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {"Authorization": f"Bearer {STRAPI_TOKEN}"}

# ───────────────── ERRORS ─────────────────
class SteamExtractorError(Exception):
    pass


# ───────────────── HELPERS ─────────────────
def extract_price(game: dict) -> dict:
    price = game.get("price_overview")

    if not price:
        return {
            "free": True,
            "currency": "",
            "original": 0,
            "final": 0,
            "discount_percent": 0,
        }

    return {
        "free": False,
        "currency": price.get("currency"),
        "original": price.get("initial", 0) // 100,
        "final": price.get("final", 0) // 100,
        "discount_percent": price.get("discount_percent", 0),
    }
    
def extract_controller_support(game: dict) -> dict:
    support = game.get("controller_support", "")

    if support:
        return {
            "supported": True,
            "type": support  # full / partial
        }

    return {
        "supported": False,
        "type": ""
    }



def extract_languages(game: dict) -> dict:
    raw = game.get("supported_languages", "")
    if not raw:
        return {
            "interface": [],
            "full_audio": [],
            "subtitles": [],
        }

    # Remove footnotes after <br>
    raw = raw.split("<br>")[0]

    interface = []
    subtitles = []
    full_audio = []

    # Match: Language + optional *
    entries = re.findall(r"([^,<]+)(<strong>\*</strong>)?", raw)

    for name, has_audio in entries:
        lang = name.strip()
        if not lang:
            continue

        interface.append(lang)
        subtitles.append(lang)

        if has_audio:
            full_audio.append(lang)

    return {
        "interface": sorted(set(interface)),
        "full_audio": sorted(set(full_audio)),
        "subtitles": sorted(set(subtitles)),
    }

def extract_features(game: dict) -> list:
    categories = game.get("categories", []) or []
    return sorted(
        {c.get("description") for c in categories if c.get("description")}
    )

def extract_genres(game: dict) -> list:
    genres = game.get("genres", []) or []
    return [g.get("description") for g in genres if g.get("description")]


def extract_release_date(game: dict) -> str:
    date_info = game.get("release_date", {})
    if not date_info or not date_info.get("date"):
        return ""

    # Steam format: "Dec 5, 2019"
    try:
        from datetime import datetime
        return datetime.strptime(date_info["date"], "%b %d, %Y").strftime("%Y-%m-%d")
    except Exception:
        return date_info["date"]

def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def extract_app_id(url: str) -> str:
    match = re.search(r"/app/(\d+)", url)
    if not match:
        raise SteamExtractorError("Invalid Steam URL")
    return match.group(1)


def clean_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"</p>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def parse_requirements_block(text: str) -> dict:
    result = {
        "os": "",
        "processor": "",
        "memory": "",
        "graphics": "",
        "storage": "",
        "directx": "",
        "network": "",
        "sound_card": "",
        "notes": "",
    }

    if not text:
        return result

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    for line in lines:
        lower = line.lower()

        if lower.startswith("os:"):
            result["os"] = line.split(":", 1)[1].strip()

        elif lower.startswith("processor:"):
            result["processor"] = line.split(":", 1)[1].strip()

        elif lower.startswith("memory:"):
            result["memory"] = line.split(":", 1)[1].strip()

        elif lower.startswith("graphics:"):
            result["graphics"] = line.split(":", 1)[1].strip()

        elif lower.startswith("storage:"):
            result["storage"] = line.split(":", 1)[1].strip()

        elif lower.startswith("directx:"):
            result["directx"] = line.split(":", 1)[1].strip()

        elif lower.startswith("network:"):
            result["network"] = line.split(":", 1)[1].strip()

        elif lower.startswith("sound"):
            result["sound_card"] = line.split(":", 1)[1].strip()

        else:
            result["notes"] += line + " "

    result["notes"] = result["notes"].strip()
    return result


def extract_system_requirements(game: dict) -> dict:
    pc_req = game.get("pc_requirements", {}) or {}

    minimum_text = clean_html(pc_req.get("minimum", ""))
    recommended_text = clean_html(pc_req.get("recommended", ""))

    return {
        "minimum": parse_requirements_block(minimum_text),
        "recommended": parse_requirements_block(recommended_text),
    }


def fetch_steam_data(app_id: str) -> dict:
    # api_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
    api_url = (f"https://store.steampowered.com/api/appdetails" f"?appids={app_id}&cc=IN&l=en")

    try:
        res = requests.get(api_url, timeout=10)
        res.raise_for_status()
        data = res.json()
    except (Timeout, RequestException, ValueError) as e:
        raise SteamExtractorError(f"Steam API error: {e}")

    if not data.get(app_id, {}).get("success"):
        raise SteamExtractorError("Steam API returned success=false")

    return data[app_id]["data"]


def build_payload(app_id: str, url: str, game: dict) -> dict:
    return {
        "app_id": app_id,
        "name": game.get("name", "Unknown"),
        "source": url,

        "developer": ", ".join(game.get("developers", [])),
        "publisher": ", ".join(game.get("publishers", [])),
        "release_date": extract_release_date(game),

        "languages": extract_languages(game),
        "genres": extract_genres(game),
        "features": extract_features(game),
        "controller_support": extract_controller_support(game),

        "price": extract_price(game),

        "system_requirements": extract_system_requirements(game),

        "images": {
            "header": game.get("header_image"),
            "screenshots": [
                s["path_full"]
                for s in game.get("screenshots", [])
                if s.get("path_full")
            ],
        },
    }


def save_json(app_id: str, payload: dict) -> None:
    path = os.path.join(OUTPUT_DIR, f"app_{app_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved → {path}")


# ─────────────── STRAPI UPLOADER ───────────────
def upload_image_to_strapi(image_url: str, game_slug: str) -> bool:
    try:
        img = requests.get(image_url, timeout=20)
        img.raise_for_status()

        filename = image_url.split("?")[0].split("/")[-1]

        files = {
            "files": (
                filename,
                img.content,
                img.headers.get("Content-Type", "image/jpeg"),
            )
        }

        res = requests.post(
            f"{STRAPI_URL}/api/upload",
            headers=HEADERS,
            files=files,
            data={"path": f"games/{game_slug}"},
            timeout=30,
        )

        res.raise_for_status()
        return True

    except RequestException as e:
        print(f"❌ Upload failed: {filename} → {e}")
        return False


def upload_images(payload: dict) -> None:
    game_slug = slugify(payload["name"])
    print(f"📁 Uploading to: games/{game_slug}")

    images = []
    if payload["images"]["header"]:
        images.append(payload["images"]["header"])
    images.extend(payload["images"]["screenshots"])

    success, failed = 0, 0

    for img in images:
        if upload_image_to_strapi(img, game_slug):
            success += 1
        else:
            failed += 1
        time.sleep(0.4)

    print(f"⬆️ Uploaded: {success} | Failed: {failed}")


# ───────────────── MAIN ─────────────────
def process_url(url: str) -> None:
    print(f"\n🔍 Processing: {url}")

    app_id = extract_app_id(url)
    game = fetch_steam_data(app_id)
    payload = build_payload(app_id, url, game)
    save_json(app_id, payload)

    print(
        f"🖼️ Extracted "
        f"{len(payload['images']['screenshots']) + (1 if payload['images']['header'] else 0)} images"
    )

    if UPLOAD_TO_STRAPI:
        upload_images(payload)


def load_urls(file_path: str) -> list:
    if not os.path.exists(file_path):
        raise SteamExtractorError("steam_links.txt not found")

    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


if __name__ == "__main__":
    urls = load_urls("steam_links.txt")

    for url in urls:
        try:
            process_url(url)
        except SteamExtractorError as e:
            print(f"❌ Error: {e}")

    print("\n🎉 Finished processing all URLs.")