# Steam

# Steam Game Data Extractor 🚀

A backend-focused Python utility that extracts **structured game data from the Steam Store API** and converts it into clean, CMS-ready JSON files.

Built for **game stores, Strapi CMS pipelines, admin tools, and automation workflows**.

---

## ✨ What This Tool Does

This script takes Steam Store URLs and extracts:

- 🎮 Game metadata (name, developer, publisher, release date)
- 💰 Steam pricing (original price, final price, discount percentage)
- 🌍 Languages grouped into:
  - Interface
  - Full Audio
  - Subtitles
- 🧩 Steam features (Single-player, Achievements, Cloud, etc.)
- 🎮 Controller support (full / partial / none)
- 🖥 Minimum & Recommended system requirements (parsed & structured)
- 🖼 Header image and screenshots
- 📦 Saves normalized JSON output
- ☁️ Optional image upload to **Strapi CMS**

This is a **backend worker script**, not a web application.

---

## 🛠 Tech Stack

- Python 3.9+
- Steam Store API
- `requests`
- `python-dotenv`
- Strapi CMS (optional)

---

## 📁 Project Structure

```bash

├── main.py # Main extractor script
├── steam_links.txt # Input: Steam game URLs
├── output/ # Generated JSON files
├── .env # Environment variables
├── requirements.txt # Python dependencies
└── README.md

```

---

## ⚙️ Installation

pip install -- All Imports

### Clone the repository

```bash
git clone https://github.com/yourusername/steam-game-data-extractor.git
cd steam-game-data-extractor

```

## 📦 Example Output

```bash
{
  "app_id": "1174180",
  "name": "Red Dead Redemption 2",
  "developer": "Rockstar Games",
  "publisher": "Rockstar Games",
  "release_date": "2019-12-05",
  "price": {
    "free": false,
    "currency": "INR",
    "original": 3199,
    "final": 1599,
    "discount_percent": 50
  },
  "languages": {
    "interface": ["English", "French"],
    "full_audio": ["English"],
    "subtitles": ["English", "French"]
  },
  "features": [
    "Single-player",
    "Steam Achievements",
    "Steam Cloud"
  ],
  "controller_support": {
    "supported": true,
    "type": "full"
  }
}

```