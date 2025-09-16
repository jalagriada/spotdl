## SpotDL

**SpotDL** is a Python-based Spotify music downloader. It retrieves track and album information directly from the Spotify API and downloads the matching audio from YouTube Music. The tool automatically embeds metadata (ID3 tags), including song title, artist, album, and album art, resulting in properly organized high-quality MP3 files (up to 320kbps). It’s an ideal solution for building an offline music collection with accurate tags and covers.

![Project Screenshot](img.png)

---

## Setup Instructions

Follow the instructions below to set up the virtual environment and install the necessary dependencies for your operating system.

## Compatible with **Linux**, **macOS**, and **Windows**.

## For Linux & macOS:
```bash
python3 -m venv spotify_venv
source spotify_venv/bin/activate
pip install spotdl
pip install requests
pip install -r requirements.txt
```

## For Windows:
```bat
python -m venv spotify_venv
call spotify_venv\Scripts\activate
pip install spotdl
pip install requests
pip install -r requirements.txt
```

## Or just do this instead on Linux and macOS:
```bash
chmod +x setup.sh   # Give execute permission
./setup.sh          # Run the script
```

## For Windows:
```bat
Simply run the batch file to automatically create the virtual environment and install all dependencies.
```

## Usage:
After setting up and activating the virtual environment, you can run spotdl scripts as needed.
- On Linux/macOS, use `python3` to ensure Python 3 is used.
- Activation commands differ between Windows (`spotify_venv\Scripts\activate`) and Linux/macOS (`source spotify_venv/bin/activate`).
- Ensure that Python and pip are installed on your system before starting.
