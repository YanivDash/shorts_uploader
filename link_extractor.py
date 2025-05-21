# File: link_extractor.py
import yt_dlp

class LinkExtractor:
    """
    Extracts YouTube Shorts URLs from a channel feed sorted by popularity and writes them to a links file.

    Parameters:
    - channel_url: Base URL of the YouTube Shorts feed (e.g., "https://www.youtube.com/@channel/shorts")
    - links_file: Path to output .txt file where links will be saved
    - sort: Sorting parameter, 'p' for popularity (default), 'd' for date
    """
    def __init__(self, channel_url: str, links_file: str, sort: str = 'p'):
        self.channel_url = channel_url.rstrip('/')
        self.links_file = links_file
        self.sort = sort

    def extract(self) -> list[str]:
        """
        Fetches the feed, extracts video IDs, constructs full short URLs,
        writes them to the links file, and returns the list of URLs.
        """
        target_url = f"{self.channel_url}?view=0&sort={self.sort}"
        ydl_opts = {
            'extract_flat': True,
            'dump_single_json': True,
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(target_url, download=False)

        entries = data.get('entries', []) or []
        links = []
        for entry in entries:
            vid = entry.get('url') or entry.get('id')
            if not vid:
                continue
            if vid.startswith('http'):
                links.append(vid)
            else:
                links.append(f"https://www.youtube.com/shorts/{vid}")

        # Save to file
        with open(self.links_file, 'w', encoding='utf-8') as f:
            f.writelines(link + '\n' for link in links)

        print(f"✅ Saved {len(links)} links to {self.links_file}")
        return links

if __name__ == "__main__":
    # Example usage
    extractor = LinkExtractor(
        channel_url="https://www.youtube.com/@sitcomhub/shorts",
        links_file="shorts_links_sitcomhub.txt"
    )
    extractor.extract()
