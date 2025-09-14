#!/usr/bin/env python3
import os
import sys
import re
import json
import requests
import subprocess
import yt_dlp
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
        print("[*] Download your song in 320kbps")
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
    
    def search_youtube(self, query: str) -> Optional[str]:
        """Search for a video on YouTube"""
        try:
            ydl_opts = {
                'quiet': True,
                'skip_download': True,
                'format': 'bestaudio/best',
                'no_progress': True,  # Disable progress bar to prevent ^[[B characters
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)
                if info['entries']:
                    return info['entries'][0]['webpage_url']
            return None
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return None
    
    def download_audio(self, url: str, output_path: Path, metadata: Dict) -> bool:
        """Download audio from YouTube"""
        try:
            # Format the output filename
            safe_artist = self.sanitize_filename(metadata['artists'])
            safe_title = self.sanitize_filename(metadata['title'])
            filename = f"{safe_artist} - {safe_title}.mp3"
            filepath = output_path / filename
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(filepath.with_suffix('.temp')),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
                'quiet': True,  # Make yt-dlp quieter
                'no_warnings': True,  # Suppress warnings
                'no_progress': True,  # Disable progress bar to prevent ^[[B characters
                'console_title': False,  # Disable console title changes
            }
            
            print("Downloading... (this may take a moment)")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Rename temp file to final filename
            temp_file = filepath.with_suffix('.temp.mp3')
            if temp_file.exists():
                temp_file.rename(filepath)
                self.apply_metadata(filepath, metadata)
                return True
            
            return False
        except Exception as e:
            print(f"Error downloading audio: {e}")
            # Clean up temporary files
            temp_file = filepath.with_suffix('.temp.mp3')
            if temp_file.exists():
                temp_file.unlink()
            return False
    
    def apply_metadata(self, filepath: Path, metadata: Dict):
        """Apply metadata to the audio file"""
        try:
            audio = MP3(filepath, ID3=ID3)
            
            # Add ID3 tag if it doesn't exist
            try:
                audio.add_tags()
            except error:
                pass
            
            # Set basic metadata
            audio['TPE1'] = TPE1(encoding=3, text=metadata['artists'])  # Artist
            audio['TIT2'] = TIT2(encoding=3, text=metadata['title'])    # Title
            audio['TALB'] = TALB(encoding=3, text=metadata.get('album', ''))  # Album
            
            if 'track_number' in metadata:
                audio['TRCK'] = mutagen.id3.TRCK(encoding=3, text=str(metadata['track_number']))
            
            if 'release_date' in metadata:
                year = metadata['release_date'].split('-')[0]
                audio['TYER'] = TYER(encoding=3, text=year)
            
            # Download and add cover art
            if 'cover_url' in metadata and metadata['cover_url']:
                try:
                    response = requests.get(metadata['cover_url'])
                    if response.status_code == 200:
                        audio['APIC'] = APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,  # 3 is for cover image
                            desc='Cover',
                            data=response.content
                        )
                except Exception as e:
                    print(f"Error adding cover art: {e}")
            
            audio.save()
        except Exception as e:
            print(f"Error applying metadata: {e}")
    
    def download_track(self, track_url: str):
        """Download a single track"""
        print(f"Processing track: {track_url}")
        
        # Get track info from Spotify
        track_info = self.get_track_info(track_url)
        if not track_info:
            print("Failed to get track information")
            return False
        
        print(f"Found track: {track_info['artists']} - {track_info['title']}")
        
        # Create search query
        search_query = f"{track_info['artists']} {track_info['title']} official audio"
        
        # Search for the track on YouTube
        print("Searching for audio on YouTube...")
        youtube_url = self.search_youtube(search_query)
        if not youtube_url:
            print("Could not find audio on YouTube")
            return False
        
        print(f"Found YouTube audio")
        
        # Create album directory
        album_dir = self.output_dir / self.sanitize_filename(track_info['album'])
        album_dir.mkdir(exist_ok=True)
        
        # Download the audio
        success = self.download_audio(youtube_url, album_dir, track_info)
        
        if success:
            print("Download completed successfully!")
        else:
            print("Download failed!")
        
        return success
    
    def download_album(self, album_url: str):
        """Download an entire album"""
        print(f"Processing album: {album_url}")
        
        # Get album info from Spotify
        album_info = self.get_album_info(album_url)
        if not album_info:
            print("Failed to get album information")
            return False
        
        print(f"Found album: {album_info['artists']} - {album_info['name']}")
        print(f"Tracks: {album_info['total_tracks']}")
        
        # Create album directory
        album_dir = self.output_dir / self.sanitize_filename(f"{album_info['artists']} - {album_info['name']}")
        album_dir.mkdir(exist_ok=True)
        
        # Add album info to each track's metadata
        for track in album_info['tracks']:
            track['album'] = album_info['name']
            track['release_date'] = album_info['release_date']
            track['cover_url'] = album_info['cover_url']
        
        # Download each track
        success_count = 0
        for i, track in enumerate(album_info['tracks']):
            print(f"\nDownloading track {i+1}/{album_info['total_tracks']}: {track['artists']} - {track['title']}")
            
            # Create search query
            search_query = f"{track['artists']} {track['title']} official audio"
            
            # Search for the track on YouTube
            youtube_url = self.search_youtube(search_query)
            if not youtube_url:
                print("Could not find audio on YouTube")
                continue
            
            # Download the audio
            success = self.download_audio(youtube_url, album_dir, track)
            
            if success:
                success_count += 1
                print("Download completed successfully!")
            else:
                print("Download failed!")
        
        print(f"\nAlbum download complete! {success_count}/{album_info['total_tracks']} tracks downloaded successfully.")
        return success_count > 0
    
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
