#!/usr/bin/env python3
import os
import sys
import re
import json
import requests
import subprocess
from pathlib import Path
from urllib.parse import quote
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import mutagen
from mutagen.id3 import ID3, TPE1, TIT2, TALB, TCON, TYER, APIC, error
from mutagen.mp3 import MP3
import argparse
from typing import List, Dict, Optional

class AdvancedSpotifyDownloader:
    def __init__(self):
        # Public Spotify API credentials (these are sample credentials)
        self.spotify_client_id = "5f573c9620494bae87890c0f08a60293"
        self.spotify_client_secret = "212476d9b0f3472eaa762d90b19b0ba8"
        
        # Set output directory to the same folder as the script
        script_dir = Path(__file__).parent.absolute()
        self.output_dir = script_dir / "Spotify Downloads"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if spotdl is installed
        if not self.check_spotdl_installed():
            print("spotdl is not installed. Please install it with: pip install spotdl")
            sys.exit(1)
        
        # Initialize Spotify client
        try:
            self.sp = spotipy.Spotify(
                auth_manager=SpotifyClientCredentials(
                    client_id=self.spotify_client_id,
                    client_secret=self.spotify_client_secret
                )
            )
        except Exception as e:
            print(f"Error initializing Spotify client: {e}")
            print("Please check your Spotify API credentials")
            sys.exit(1)
    
    def check_spotdl_installed(self) -> bool:
        """Check if spotdl is installed and available"""
        try:
            subprocess.run(["spotdl", "--version"], 
                          capture_output=True, check=True, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def clear_screen(self):
        """Clear the screen but keep the header"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.show_header()
    
    def show_header(self):
        """Display the header"""
        print(r"                  _      _ _ ")
        print(r"                 | |    | | |")
        print(r"  ___ _ __   ___ | |_ __| | |")
        print(r" / __| '_ \ / _ \| __/ _` | |")
        print(r" \__ \ |_) | (_) | || (_| | |")
        print(r" |___/ .__/ \___/ \__\__,_|_|")
        print(r"     | |                     ")
        print(r"     |_|                     ")
        print("     Developed by: @jalagriada")
        print()
        print("[*] Spotify Music Downloader")
        print("[*] Download your song in 320kbps using spotdl")
        print("[*] Paste Spotify URLs (track or album). Type 'exit' to quit.")
        print("[*] Type 'clear' to clear the screen.")
        print(f"[*] Downloading to: {self.output_dir}")
        print("-" * 50)
    
    def sanitize_filename(self, name: str) -> str:
        """Remove invalid characters from filename"""
        return re.sub(r'[<>:"/\\|?*]', '', name)
    
    def get_track_info(self, track_url: str) -> Optional[Dict]:
        """Get track information from Spotify"""
        try:
            track_id = track_url.split('/')[-1].split('?')[0]
            track = self.sp.track(track_id)
            
            # Format artists as comma-separated list
            artists = ", ".join([artist['name'] for artist in track['artists']])
            
            return {
                'id': track['id'],
                'title': track['name'],
                'artists': artists,
                'album': track['album']['name'],
                'release_date': track['album']['release_date'],
                'track_number': track['track_number'],
                'duration_ms': track['duration_ms'],
                'cover_url': track['album']['images'][0]['url'] if track['album']['images'] else None
            }
        except Exception as e:
            print(f"Error getting track info: {e}")
            return None
    
    def get_album_info(self, album_url: str) -> Optional[Dict]:
        """Get album information from Spotify"""
        try:
            album_id = album_url.split('/')[-1].split('?')[0]
            album = self.sp.album(album_id)
            
            # Get all tracks from the album
            tracks = []
            results = self.sp.album_tracks(album_id)
            tracks.extend(results['items'])
            
            while results['next']:
                results = self.sp.next(results)
                tracks.extend(results['items'])
            
            album_info = {
                'id': album['id'],
                'name': album['name'],
                'artists': ", ".join([artist['name'] for artist in album['artists']]),
                'release_date': album['release_date'],
                'total_tracks': album['total_tracks'],
                'cover_url': album['images'][0]['url'] if album['images'] else None,
                'tracks': []
            }
            
            for track in tracks:
                track_artists = ", ".join([artist['name'] for artist in track['artists']])
                album_info['tracks'].append({
                    'id': track['id'],
                    'title': track['name'],
                    'artists': track_artists,
                    'track_number': track['track_number'],
                    'duration_ms': track['duration_ms']
                })
            
            return album_info
        except Exception as e:
            print(f"Error getting album info: {e}")
            return None
    
    def download_with_spotdl(self, url: str, output_path: Path) -> bool:
        """Download audio using spotdl with 320kbps quality and custom filename format"""
        try:
            # Change to the output directory
            original_cwd = os.getcwd()
            os.chdir(output_path)
            
            # First, let spotdl download with its default format
            result = subprocess.run(
                ["spotdl", url, "--bitrate", "320k"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Change back to original directory
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                # Now rename the files to use comma instead of slash
                self.rename_files_with_commas(output_path)
                # Fix metadata to use commas instead of slashes
                self.fix_metadata_commas(output_path)
                print("Download completed successfully!")
                return True
            else:
                print(f"spotdl error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("Download timed out!")
            os.chdir(original_cwd)
            return False
        except Exception as e:
            print(f"Error downloading with spotdl: {e}")
            os.chdir(original_cwd)
            return False
    
    def rename_files_with_commas(self, directory: Path):
        """Rename files to replace slashes with commas in artist names"""
        for file_path in directory.glob("*.mp3"):
            if " - " in file_path.name and "/" in file_path.name:
                # Replace slashes with commas in the filename
                new_name = file_path.name.replace("/", ", ")
                new_path = directory / new_name
                
                # Avoid overwriting existing files
                counter = 1
                while new_path.exists():
                    name_parts = new_name.rsplit('.', 1)
                    new_name = f"{name_parts[0]} ({counter}).{name_parts[1]}"
                    new_path = directory / new_name
                    counter += 1
                
                try:
                    file_path.rename(new_path)
                    print(f"Renamed: {file_path.name} -> {new_name}")
                except Exception as e:
                    print(f"Error renaming file {file_path.name}: {e}")
    
    def fix_metadata_commas(self, directory: Path):
        """Fix ID3 metadata to use commas instead of slashes for artist names"""
        for file_path in directory.glob("*.mp3"):
            try:
                audio = MP3(file_path, ID3=ID3)
                
                # Ensure ID3 tags exist
                try:
                    audio.add_tags()
                except error:
                    pass  # Tags already exist
                
                # Fix artist metadata if it contains slashes
                if 'TPE1' in audio.tags:
                    artist = audio.tags['TPE1'].text[0]
                    if '/' in artist:
                        fixed_artist = artist.replace('/', ', ')
                        audio.tags['TPE1'] = TPE1(encoding=3, text=fixed_artist)
                        print(f"Fixed artist metadata: {artist} -> {fixed_artist}")
                
                # Save changes
                audio.save()
                
            except Exception as e:
                print(f"Error fixing metadata for {file_path.name}: {e}")
    
    def download_track(self, track_url: str):
        """Download a single track using spotdl"""
        print(f"Processing track: {track_url}")
        
        # Get track info from Spotify (for display purposes)
        track_info = self.get_track_info(track_url)
        if not track_info:
            print("Failed to get track information")
            return False
        
        print(f"Found track: {track_info['artists']} - {track_info['title']}")
        
        # Create album directory
        album_dir = self.output_dir / self.sanitize_filename(track_info['album'])
        album_dir.mkdir(exist_ok=True)
        
        # Download the audio using spotdl
        success = self.download_with_spotdl(track_url, album_dir)
        
        if success:
            print("Download completed successfully!")
        else:
            print("Download failed!")
        
        return success
    
    def download_album(self, album_url: str):
        """Download an entire album using spotdl"""
        print(f"Processing album: {album_url}")
        
        # Get album info from Spotify (for display purposes)
        album_info = self.get_album_info(album_url)
        if not album_info:
            print("Failed to get album information")
            return False
        
        print(f"Found album: {album_info['artists']} - {album_info['name']}")
        print(f"Tracks: {album_info['total_tracks']}")
        
        # Create album directory
        album_dir = self.output_dir / self.sanitize_filename(f"{album_info['artists']} - {album_info['name']}")
        album_dir.mkdir(exist_ok=True)
        
        # Download the entire album using spotdl
        success = self.download_with_spotdl(album_url, album_dir)
        
        if success:
            print("Album download completed successfully!")
        else:
            print("Album download failed!")
        
        return success
    
    def process_url(self, url: str):
        """Process a Spotify URL (track or album)"""
        if 'track' in url:
            return self.download_track(url)
        elif 'album' in url:
            return self.download_album(url)
        else:
            print("Unsupported Spotify URL. Please provide a track or album link.")
            return False

def main():
    parser = argparse.ArgumentParser(description='Advanced Spotify Downloader')
    parser.add_argument('url', nargs='?', help='Spotify track or album URL')
    parser.add_argument('--file', '-f', help='Text file containing multiple Spotify URLs')
    
    args = parser.parse_args()
    
    downloader = AdvancedSpotifyDownloader()
    
    if args.file:
        # Process multiple URLs from a file
        try:
            with open(args.file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            for url in urls:
                print(f"\n{'='*50}")
                downloader.process_url(url)
                print(f"{'='*50}\n")
                
        except FileNotFoundError:
            print(f"File not found: {args.file}")
        except Exception as e:
            print(f"Error processing file: {e}")
    
    elif args.url:
        # Process a single URL
        downloader.process_url(args.url)
    
    else:
        # Interactive mode
        downloader.show_header()
        
        while True:
            try:
                url = input("\nEnter Spotify URL: ").strip()
                
                if url.lower() in ['exit', 'quit', 'q']:
                    break
                
                if url.lower() in ['clear', 'cls']:
                    downloader.clear_screen()
                    continue
                
                if not url:
                    continue
                
                downloader.process_url(url)
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()
