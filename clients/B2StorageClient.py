import os
import hashlib
from typing import Optional, Dict
from b2sdk.v2 import B2Api, InMemoryAccountInfo
from b2sdk.v2.exception import NonExistentBucket


class B2StorageClient:
    """
    Client for uploading files to Backblaze B2 cloud storage.

    This client handles:
    - Authentication with Backblaze B2
    - File uploads with progress tracking
    - Automatic bucket creation
    - File deletion after successful upload
    - Public URL generation for uploaded files
    """

    def __init__(
        self,
        application_key_id: Optional[str] = None,
        application_key: Optional[str] = None,
        bucket_name: Optional[str] = None
    ):
        """
        Initialize B2 Storage Client.

        Args:
            application_key_id: B2 application key ID (or set B2_APPLICATION_KEY_ID env var)
            application_key: B2 application key (or set B2_APPLICATION_KEY env var)
            bucket_name: B2 bucket name (or set B2_BUCKET_NAME env var)

        Raises:
            ValueError: If credentials are not provided
        """
        self.application_key_id = application_key_id or os.getenv("B2_APPLICATION_KEY_ID")
        self.application_key = application_key or os.getenv("B2_APPLICATION_KEY")
        self.bucket_name = bucket_name or os.getenv("B2_BUCKET_NAME")

        if not self.application_key_id or not self.application_key:
            raise ValueError(
                "B2 credentials must be provided via parameters or environment variables "
                "(B2_APPLICATION_KEY_ID and B2_APPLICATION_KEY)"
            )

        if not self.bucket_name:
            raise ValueError(
                "B2 bucket name must be provided via parameter or B2_BUCKET_NAME environment variable"
            )

        # Initialize B2 API
        self.info = InMemoryAccountInfo()
        self.b2_api = B2Api(self.info)
        self.bucket = None
        self._authenticated = False

    def authenticate(self):
        """
        Authenticate with Backblaze B2 and get the bucket.

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return

        print(f"🔐 Authenticating with Backblaze B2...")
        self.b2_api.authorize_account("production", self.application_key_id, self.application_key)

        try:
            self.bucket = self.b2_api.get_bucket_by_name(self.bucket_name)
            print(f"✅ Connected to bucket: {self.bucket_name}")
        except NonExistentBucket:
            print(f"⚠️  Bucket '{self.bucket_name}' does not exist. Creating it...")
            self.bucket = self.b2_api.create_bucket(
                self.bucket_name,
                bucket_type='allPrivate'  # Can be 'allPublic' if you want public URLs
            )
            print(f"✅ Created bucket: {self.bucket_name}")

        self._authenticated = True

    def upload_file(
        self,
        local_file_path: str,
        remote_file_name: Optional[str] = None,
        delete_local: bool = True
    ) -> Dict[str, str]:
        """
        Upload a file to Backblaze B2.

        Args:
            local_file_path: Path to the local file to upload
            remote_file_name: Name to give the file in B2 (defaults to basename of local file)
            delete_local: If True, delete the local file after successful upload

        Returns:
            Dictionary with upload information:
            {
                'file_id': 'B2 file ID',
                'file_name': 'filename in B2',
                'content_type': 'video/mp4',
                'size': file_size_in_bytes,
                'url': 'download URL',
                'local_deleted': True/False
            }

        Raises:
            FileNotFoundError: If local file doesn't exist
            Exception: If upload fails
        """
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"Local file not found: {local_file_path}")

        # Authenticate if not already done
        if not self._authenticated:
            self.authenticate()

        # Determine remote file name
        if remote_file_name is None:
            remote_file_name = os.path.basename(local_file_path)

        # Get file info
        file_size = os.path.getsize(local_file_path)
        file_size_mb = file_size / (1024 * 1024)

        print(f"📤 Uploading {local_file_path} ({file_size_mb:.2f} MB) to B2...")
        print(f"   Remote name: {remote_file_name}")

        # Upload the file
        try:
            uploaded_file = self.bucket.upload_local_file(
                local_file=local_file_path,
                file_name=remote_file_name,
                content_type='video/mp4'  # Adjust if you upload other file types
            )

            print(f"✅ Upload successful!")
            print(f"   File ID: {uploaded_file.id_}")
            print(f"   File Name: {uploaded_file.file_name}")

            # Generate download URL
            download_url = self.b2_api.get_download_url_for_file_name(
                self.bucket_name,
                uploaded_file.file_name
            )

            result = {
                'file_id': uploaded_file.id_,
                'file_name': uploaded_file.file_name,
                'content_type': uploaded_file.content_type,
                'size': uploaded_file.size,
                'url': download_url,
                'local_deleted': False
            }

            # Delete local file if requested
            if delete_local:
                try:
                    os.remove(local_file_path)
                    print(f"🗑️  Deleted local file: {local_file_path}")
                    result['local_deleted'] = True
                except Exception as e:
                    print(f"⚠️  Warning: Could not delete local file: {e}")
                    result['local_deleted'] = False

            return result

        except Exception as e:
            print(f"❌ Upload failed: {e}")
            raise

    def generate_download_url(self, file_name: str, valid_duration_seconds: int = 3600) -> str:
        """
        Generate a download URL for a file in B2.

        Args:
            file_name: Name of the file in B2
            valid_duration_seconds: How long the URL should be valid (default: 1 hour)

        Returns:
            Download URL string

        Note:
            For public buckets, this returns a permanent URL.
            For private buckets, you would need to generate an authorization token.
        """
        if not self._authenticated:
            self.authenticate()

        return self.b2_api.get_download_url_for_file_name(
            self.bucket_name,
            file_name
        )

    def list_files(self, max_files: int = 100, prefix: str = None) -> list:
        """
        List files in the B2 bucket.

        Args:
            max_files: Maximum number of files to return
            prefix: Optional prefix to filter files

        Returns:
            List of file information dictionaries
        """
        if not self._authenticated:
            self.authenticate()

        files = []
        for file_version, _ in self.bucket.ls(max_file_count=max_files):
            if prefix is None or file_version.file_name.startswith(prefix):
                files.append({
                    'file_id': file_version.id_,
                    'file_name': file_version.file_name,
                    'size': file_version.size,
                    'upload_timestamp': file_version.upload_timestamp
                })

        return files

    def delete_file(self, file_name: str, file_id: str):
        """
        Delete a file from B2.

        Args:
            file_name: Name of the file to delete
            file_id: B2 file ID

        Returns:
            None
        """
        if not self._authenticated:
            self.authenticate()

        self.b2_api.delete_file_version(file_id, file_name)
        print(f"🗑️  Deleted file from B2: {file_name}")


def upload_video_to_b2(
    video_path: str,
    remote_name: Optional[str] = None,
    delete_local: bool = True,
    application_key_id: Optional[str] = None,
    application_key: Optional[str] = None,
    bucket_name: Optional[str] = None
) -> Dict[str, str]:
    """
    Convenience function to upload a video to Backblaze B2.

    Args:
        video_path: Path to the local video file
        remote_name: Name to give the file in B2 (optional)
        delete_local: Whether to delete the local file after upload
        application_key_id: B2 application key ID (optional if env var set)
        application_key: B2 application key (optional if env var set)
        bucket_name: B2 bucket name (optional if env var set)

    Returns:
        Dictionary with upload information

    Example:
        >>> result = upload_video_to_b2("output_video.mp4", delete_local=True)
        >>> print(f"Video URL: {result['url']}")
    """
    client = B2StorageClient(
        application_key_id=application_key_id,
        application_key=application_key,
        bucket_name=bucket_name
    )

    return client.upload_file(video_path, remote_name, delete_local)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python B2StorageClient.py <video_file_path> [remote_name]")
        print("\nEnvironment variables required:")
        print("  B2_APPLICATION_KEY_ID")
        print("  B2_APPLICATION_KEY")
        print("  B2_BUCKET_NAME")
        sys.exit(1)

    video_file = sys.argv[1]
    remote_name = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        result = upload_video_to_b2(video_file, remote_name, delete_local=False)
        print("\n" + "=" * 60)
        print("📋 Upload Summary:")
        print("=" * 60)
        print(f"File ID: {result['file_id']}")
        print(f"File Name: {result['file_name']}")
        print(f"Size: {result['size'] / (1024*1024):.2f} MB")
        print(f"URL: {result['url']}")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
