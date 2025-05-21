# File: main.py
import os
import yaml
from link_extractor import LinkExtractor
from downloader import Downloader
from auth import get_youtube_client_from_env
from uploader import YouTubeUploader
from googleapiclient.errors import HttpError
from googleapiclient.http import ResumableUploadError

CONFIG_FILE = 'config.yml'

def main():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as cf:
        cfg = yaml.safe_load(cf)

    for ch in cfg['channels']:
        name = ch['name']
        print(f"\n=== Channel: {name} ===")

        base = ch['base_folder']
        os.makedirs(base, exist_ok=True)

        links_file   = os.path.join(base, ch['links_file'])
        video_folder = os.path.join(base, ch['video_folder'])
        # token_file   = os.path.join(base, ch['token'])
        os.makedirs(video_folder, exist_ok=True)

        # 1) Extract links if needed
        if not os.path.exists(links_file) or os.path.getsize(links_file) == 0:
            print("⬇️ Extracting shorts links...")
            LinkExtractor(ch['channel_url'], links_file,
                          sort=ch.get('sort','p')).extract()
        else:
            print("✅ Links exist; skipping extraction.")

        # 2) Download up to download_count new videos
        existing = [f for f in os.listdir(video_folder)
                    if f.lower().endswith('.mp4')]
        to_dl = ch.get('download_count', 1) - len(existing)
        if to_dl > 0:
            print(f"⬇️ Downloading {to_dl} video(s)...")
            Downloader(
                links_file=links_file,
                video_folder=video_folder,
                max_downloads=to_dl,
                max_attempts=ch.get('max_attempts', 10),
                sleep_between=ch.get('sleep_between', 3)
            ).download_with_retries()
        else:
            print("✅ No downloads needed.")

        # 3) Authenticate via token.json only
        yt = get_youtube_client_from_env(ch['token_env'])
        uploader = YouTubeUploader(
            youtube=yt,
            category_id=ch.get('category_id','23'),
            tags=ch.get('tags',['shorts'])
        )

        # 4) Upload up to upload_count videos, handling quota errors gracefully
        mp4s = [f for f in os.listdir(video_folder)
                if f.lower().endswith('.mp4')]
        for fname in mp4s[: ch.get('upload_count', 1) ]:
            path = os.path.join(video_folder, fname)
            try:
                uploader.upload_and_cleanup(path)

            except (ResumableUploadError, HttpError) as e:
                # Extract HTTP status if possible
                status = None
                if hasattr(e, 'resp') and getattr(e.resp, 'status', None):
                    status = e.resp.status
                msg = str(e)

                if status == 400 and 'uploadLimitExceeded' in msg:
                    print(f"⚠️ Upload limit exceeded for channel '{name}'. "
                          "Skipping remaining uploads.")
                    break
                else:
                    print(f"⚠️ Error uploading '{fname}' for channel '{name}': {msg}")
                    # continue to next video in this channel
                    continue

        print(f"--- Done processing channel: {name} ---")

if __name__ == '__main__':
    main()
