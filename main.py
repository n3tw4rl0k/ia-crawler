import os
import requests
from urllib.parse import quote
import time


def download_internet_archive_episodes(base_url, start_episode, end_episode, output_dir):
    """
    Downloads episodes from Internet Archive based on a given URL pattern.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def get_filename_patterns(episode_num):
        if episode_num < 10:
            return [
                f"Saiyuki vol {str(episode_num).zfill(2)}.mp4",  # 01
                f"Saiyuki vol {episode_num}.mp4",  # 1
                f"Saiyuki vol {str(episode_num).zfill(3)}.mp4",  # 001
                f"Saiyuki {str(episode_num).zfill(2)}.mp4",  # Saiyuki 01.mp4
                f"Saiyuki {episode_num}.mp4",  # Saiyuki 1.mp4
                f"Saiyuki-{str(episode_num).zfill(2)}.mp4",  # Saiyuki-01.mp4
                f"Saiyuki-{episode_num}.mp4",  # Saiyuki-1.mp4
            ]
        elif episode_num < 100:
            return [
                f"Saiyuki vol {str(episode_num).zfill(2)}.mp4",  # 01
                f"Saiyuki vol {episode_num}.mp4",  # 1
                f"Saiyuki vol {str(episode_num).zfill(3)}.mp4",  # 001
                f"Saiyuki {str(episode_num).zfill(2)}.mp4",  # Saiyuki 01.mp4
                f"Saiyuki-{str(episode_num).zfill(2)}.mp4",  # Saiyuki-01.mp4
            ]
        else:
            return [
                f"Saiyuki vol {episode_num}.mp4",  # 100
                f"Saiyuki vol {str(episode_num).zfill(3)}.mp4",  # 100
                f"Saiyuki {episode_num}.mp4",  # Saiyuki 100.mp4
                f"Saiyuki-{episode_num}.mp4",  # Saiyuki-100.mp4
            ]

    pattern_cache = {}

    for episode_num in range(start_episode, end_episode + 1):
        output_filename = f"Saiyuki vol {episode_num}.mp4"
        output_path = os.path.join(output_dir, output_filename)

        if os.path.exists(output_path):
            print(f"Skipping {output_filename} - already downloaded.")
            continue

        found = False
        similar_episode = None

        for cached_num in sorted(pattern_cache.keys(), key=lambda x: abs(x - episode_num)):
            if abs(cached_num - episode_num) < 10:  # Look for patterns from nearby episodes
                similar_episode = cached_num
                break

        filename_patterns = get_filename_patterns(episode_num)

        if similar_episode is not None:
            pattern = pattern_cache[similar_episode]
            if pattern in filename_patterns:
                filename_patterns.remove(pattern)
                filename_patterns.insert(0, pattern)

        # Try all patterns until one works
        for filename in filename_patterns:
            url_encoded_filename = quote(filename)
            episode_url = f"{base_url.rstrip('/')}/{url_encoded_filename}"

            try:
                print(f"Trying {episode_url}...")
                head_response = requests.head(episode_url)
                if head_response.status_code != 200:
                    continue

                print(f"Downloading {filename} to {output_path}...")
                response = requests.get(episode_url, stream=True)
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0

                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            # Print progress
                            if total_size > 0:
                                progress = (downloaded_size / total_size) * 100
                                print(f"\rProgress: {progress:.1f}%", end="")

                print(f"\nDownloaded {filename} successfully!")
                found = True
                pattern_cache[episode_num] = filename  # Cache the successful pattern
                break

            except requests.exceptions.RequestException as e:
                print(f"Pattern {filename} failed: {e}")
                continue
            except IOError as e:
                print(f"Error saving {filename}: {e}")
                if os.path.exists(output_path):
                    os.remove(output_path)
                    print(f"Removed partial file: {output_path}")
                break

        if not found:
            print(f"ERROR: Could not find any working URL for episode {episode_num}. Tried all patterns.")
            # Optional: Write to a log file of missing episodes
            with open(os.path.join(output_dir, "missing_episodes.txt"), "a") as log:
                log.write(f"Episode {episode_num} not found\n")

        time.sleep(1)


# Example usage, this default will download all Gensoumaden Saiyuki episodes
base_url = "https://ia601301.us.archive.org/1/items/saiyuki-adv-dvds/"
start_episode = 1
end_episode = 129
output_directory = "Saiyuki_Episodes"

download_internet_archive_episodes(base_url, start_episode, end_episode, output_directory)
