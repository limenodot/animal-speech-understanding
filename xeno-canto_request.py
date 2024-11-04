import requests
import time
import pandas as pd
import os
from tqdm import tqdm
import argparse

BASE_URL = "https://xeno-canto.org/api/2/recordings"

def get_recordings(query, max_pages=1):
    """
    Fetch recordings from Xeno-canto API based on a search query.
    
    Parameters:
    - query (str): Search string following Xeno-canto's format.
    - max_pages (int): Maximum number of pages to retrieve.

    Returns:
    - list: List of recording JSON objects.
    """
    recordings = []
    page = 1
    
    while page <= max_pages:
        url = f"{BASE_URL}?query={query}&page={page}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            recordings.extend(data.get("recordings", []))

            if page >= int(data["numPages"]):
                break
            
            page += 1
            time.sleep(1)
        
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            break

    return recordings

def save_recordings_to_csv(recordings, filename="xeno-canto/recordings.csv"):
    """
    Save recording data to a CSV file.
    
    Parameters:
    - recordings (list): List of recording JSON objects.
    - filename (str): Filename for the CSV file.
    """
    if not os.path.exists("xeno-canto"):
        os.makedirs("xeno-canto")
    
    flattened_data = []
    for record in recordings:
        flattened_record = {
            "id": record.get("id"),
            "gen": record.get("gen"),
            "sp": record.get("sp"),
            "ssp": record.get("ssp"),
            "group": record.get("group"),
            "en": record.get("en"),
            "rec": record.get("rec"),
            "cnt": record.get("cnt"),
            "loc": record.get("loc"),
            "lat": record.get("lat"),
            "lng": record.get("lng"),
            "alt": record.get("alt"),
            "type": record.get("type"),
            "sex": record.get("sex"),
            "stage": record.get("stage"),
            "method": record.get("method"),
            "url": record.get('url'),
            "file": record.get('file'),
            "file-name": record.get("file-name"),
            "sono_small": record['sono'].get('small') if record.get("sono") else None,
            "sono_med": record['sono'].get('med') if record.get("sono") else None,
            "sono_large": record['sono'].get('large') if record.get("sono") else None,
            "sono_full": record['sono'].get('full') if record.get("sono") else None,
            "osci_small": record['osci'].get('small') if record.get("osci") else None,
            "osci_med": record['osci'].get('med') if record.get("osci") else None,
            "osci_large": record['osci'].get('large') if record.get("osci") else None,
            "lic": record.get('lic'),
            "q": record.get("q"),
            "length": record.get("length"),
            "time": record.get("time"),
            "date": record.get("date"),
            "uploaded": record.get("uploaded"),
            "also": ", ".join(record.get("also", [])),
            "rmk": record.get("rmk"),
            "bird-seen": record.get("bird-seen"),
            "animal-seen": record.get("animal-seen"),
            "playback-used": record.get("playback-used"),
            "temp": record.get("temp"),
            "regnr": record.get("regnr"),
            "auto": record.get("auto"),
            "dvc": record.get("dvc"),
            "mic": record.get("mic"),
            "smp": record.get("smp"),
        }
        flattened_data.append(flattened_record)

    df = pd.DataFrame(flattened_data)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"Recordings is saved into {filename}")

def download_audio_files(csv_filename, output_dir="xeno-canto/audio_files"):
    """
    Downloads audio files listed in a CSV file and saves them to the specified directory.

    Parameters:
    - csv_filename (str): The path to the CSV file containing audio metadata. 
                          The file should include columns 'file' (audio file URL) and 'file-name' (original file name).
    - output_dir (str): The directory to save downloaded audio files. Default is 'audio_files'.
    """
    df = pd.read_csv(csv_filename)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    for _, row in tqdm(df.iterrows(), desc='Downloading audio recordings', total=len(df)):
        file_url = row["file"]
        file_name = row["file-name"]
        
        output_path = os.path.join(output_dir, file_name)
        
        try:
            response = requests.get(file_url)
            response.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(response.content)
        
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {file_name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and save audio recordings from Xeno-canto.")
    parser.add_argument("--max_pages", type=int, help="Maximum number of pages to retrieve.", default=1)
    parser.add_argument("--filename", type=str, help="Filename for the CSV file to save recordings.", default="xeno-canto/recordings.csv")
    parser.add_argument("--output_dir", type=str, help="Directory to save downloaded audio files.", default="xeno-canto/audio_files")
    parser.add_argument("--query", type=str, help="Query with specific filters.")

    args = parser.parse_args()

    recordings = get_recordings(args.query, max_pages=args.max_pages)
    save_recordings_to_csv(recordings, filename=args.filename)
    download_audio_files(args.filename, output_dir=args.output_dir)
