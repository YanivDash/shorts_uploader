# File: uploader.py
import os
import time
import googleapiclient.http

class YouTubeUploader:
    """
    Uploads videos via a pre-authenticated `youtube` client and deletes them locally.
    """
    def __init__(self, youtube, category_id: str = '23', tags: list[str] = None):
        self.youtube = youtube
        self.category_id = category_id
        self.tags = tags or ['shorts']

    def upload_and_cleanup(self, video_path: str, delete_retries: int = 30, retry_delay: int = 1):
        title = os.path.splitext(os.path.basename(video_path))[0]
        media = googleapiclient.http.MediaFileUpload(
            video_path, chunksize=-1, resumable=True, mimetype='video/mp4'
        )
        request = self.youtube.videos().insert(
            part='snippet,status',
            body={
                'snippet': {
                    'title': title,
                    'categoryId': self.category_id,
                    'tags': self.tags
                },
                'status': {
                    'privacyStatus': 'public',
                    'madeForKids': False
                }
            },
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"⌛ Uploading {title}: {int(status.progress() * 100)}%")

        print(f"✅ Uploaded: {title} (ID: {response['id']})")

        # Close file handle
        if hasattr(media, '_fd') and media._fd:
            media._fd.close()

        # Delete local file with retries
        for i in range(delete_retries):
            try:
                os.remove(video_path)
                print(f"🧹 Deleted: {video_path}")
                break
            except (PermissionError, OSError) as e:
                print(f"⚠️ Retry {i+1}: {e}")
                time.sleep(retry_delay)
        else:
            print(f"⚠️ Could not delete {video_path} after {delete_retries} retries")


    
if __name__ == "__main__":
    # Example usage; replace with actual paths and desired category/tags
    uploader = YouTubeUploader(
        client_secret_file='client_secret.json',
        token_file='token.json',
        category_id='22',       # People & Blogs
        tags=['shorts', 'funny']
    )
    yt = uploader.authenticate()
    videos_folder = 'videos'
    for fname in os.listdir(videos_folder):
        if fname.lower().endswith('.mp4'):
            path = os.path.join(videos_folder, fname)
            try:
                uploader.upload_and_cleanup(path)
            except Exception as e:
                print(f"❌ Error uploading {fname}: {e}")
