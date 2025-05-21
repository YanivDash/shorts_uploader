# File: downloader.py
import os
import time
import yt_dlp

class Downloader:
    """
    Downloads YouTube Shorts from a links file, retrying on failure, and ensures a target number of videos are downloaded.

    Parameters:
    - links_file: Path to the .txt file containing video URLs
    - video_folder: Directory to save downloaded videos
    - max_downloads: Number of successful downloads to achieve
    - max_attempts: Total attempts (success+failure) before giving up
    - sleep_between: Seconds to wait between successful downloads
    """
    def __init__(self,
                 links_file: str,
                 video_folder: str,
                 max_downloads: int = 5,
                 max_attempts: int = 10,
                 sleep_between: int = 3):
        self.links_file = links_file
        self.video_folder = video_folder
        self.max_downloads = max_downloads
        self.max_attempts = max_attempts
        self.sleep_between = sleep_between
        os.makedirs(self.video_folder, exist_ok=True)

    def _read_links(self) -> list[str]:
        with open(self.links_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]

    def _write_links(self, links: list[str]):
        with open(self.links_file, 'w', encoding='utf-8') as f:
            f.writelines(link + '\n' for link in links)

    def _download_one(self, url: str) -> bool:
        """Attempt to download a single video URL using yt_dlp."""
        opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{self.video_folder}/%(title)s.%(ext)s',
            'quiet': True,             # no stdout except errors
            'no_warnings': True,       # suppress warning messages
            'ignoreerrors': False,     # still stop on real errors
            'verbose': False,  
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            print(f"✅ Downloaded: {url}")
            return True
        except Exception as e:
            print(f"❌ Failed: {url} | {e}")
            return False

    def download_with_retries(self):
        """
        Process the links file, attempting downloads from the end of the list.
        Continues until max_downloads successes or max_attempts total tries.
        Updates links_file by removing each attempted URL.
        """
        success_count = 0
        attempt_count = 0

        while success_count < self.max_downloads and attempt_count < self.max_attempts:
            links = self._read_links()
            if not links:
                print("📂 No more links to process.")
                break

            url = links[-1]  # pick last link
            print(f"\n▶️ Attempt #{attempt_count+1}: {url}")

            ok = self._download_one(url)
            # remove link regardless of success or failure
            links.pop()
            self._write_links(links)

            attempt_count += 1
            if ok:
                success_count += 1
                time.sleep(self.sleep_between)

        print(f"\n🎉 Finished: {success_count}/{self.max_downloads} downloaded after {attempt_count} attempts.")

if __name__ == "__main__":
    # Example usage; adjust paths and parameters as needed
    downloader = Downloader(
        links_file='shorts_links.txt',
        video_folder='videos',
        max_downloads=5,
        max_attempts=10,
        sleep_between=3
    )
    downloader.download_with_retries()
