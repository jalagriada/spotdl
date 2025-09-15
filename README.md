# spotdl

A Python-based Spotify downloader that fetches high-quality (320kbps) MP3 audio from Spotify tracks and albums. It uses the Spotify API for track info, YouTube for audio search, and yt-dlp for downloads. Supports metadata embedding (ID3 tags) including album art. Ideal for offline music collections.

![Project Screenshot](img.png)

---

## Setup Instructions

Follow the instructions below to set up the virtual environment and install the necessary dependencies based on your operating system.

### Compatible with **Linux**, **macOS**, and **Windows**.

## For Linux & macOS:
python3 -m venv spotify_venv
source spotify_venv/bin/activate
pip install spotdl
pip install requests
pip install -r requirements.txt

## For Windows: 
python -m venv spotify_venv
spotify_venv\Scripts\activate
pip install spotdl
pip install requests
pip install -r requirements.txt

## Or just do this instead:
chmod +x setup.sh   # give execute permission
./setup.sh          # run the script

## For Windows:
Jus run the batch file to fully execute all the requirements.

## Usage:
After setting up and activating the virtual environment, you can run spotdl scripts as needed.
- On Linux/macOS, python3 is recommended to ensure you are using Python 3.
- The activation command differs between Windows (spotify_venv\Scripts\activate) and Linux/macOS (source spotify_venv/bin/activate).
- Make sure you have Python and pip installed on your system before starting.
