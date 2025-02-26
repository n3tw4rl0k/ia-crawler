import os
import requests
from urllib.parse import urljoin

def download_internet_archive_episodes(base_url, start_episode, end_episode, output_dir):
    """
    Downloads episodes from Internet Archive based on a given URL pattern.
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for episode_num in range(start_episode, end_episode + 1):
        episode_str = str(episode_num).zfill(2)
        filename = f"Saiyuki vol {episode_str}.mp4"
        episode_url = urljoin(base_url, filename)

        output_path = os.path.join(output_dir, filename)

        try:
            print(f"Downloading {episode_url} to {output_path}...")
            response = requests.get(episode_url, stream=True)
            response.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"Downloaded {filename} successfully!")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {filename}: {e}")
        except IOError as e:
            print(f"Error saving {filename}: {e}")

# Example usage, this default will download all Gensoumaden Saiyuki episodes
base_url = "https://ia601301.us.archive.org/1/items/saiyuki-adv-dvds/"
start_episode = 1
end_episode = 129
output_directory = "Saiyuki_Episodes"

download_internet_archive_episodes(base_url, start_episode, end_episode, output_directory)
