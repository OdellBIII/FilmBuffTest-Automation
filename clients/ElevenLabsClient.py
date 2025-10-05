import os
import requests
import tempfile
from typing import Optional

class ElevenLabsClient:
    """Client for Eleven Labs text-to-speech API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }

        # Default voice ID (Rachel - a natural sounding female voice)
        # You can change this to other voice IDs from Eleven Labs
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"

    def text_to_speech(self, text: str, voice_id: Optional[str] = None, save_path: Optional[str] = None) -> str:
        """
        Convert text to speech using Eleven Labs API

        Args:
            text (str): Text to convert to speech
            voice_id (str, optional): Voice ID to use. Defaults to Rachel voice.
            save_path (str, optional): Path to save the audio file. If None, creates temp file.

        Returns:
            str: Path to the generated audio file

        Raises:
            Exception: If API request fails
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")

        # Use default voice if none specified
        if voice_id is None:
            voice_id = self.default_voice_id

        # API endpoint for text-to-speech
        url = f"{self.base_url}/text-to-speech/{voice_id}"

        # Request payload
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        try:
            # Make API request
            response = requests.post(url, json=data, headers=self.headers, timeout=30)

            if response.status_code == 200:
                # Create save path if not provided
                if save_path is None:
                    # Create temporary file with .mp3 extension
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                    save_path = temp_file.name
                    temp_file.close()

                # Ensure directory exists
                directory = os.path.dirname(save_path)
                if directory:  # Only create directory if save_path has a directory component
                    os.makedirs(directory, exist_ok=True)

                # Save audio content
                with open(save_path, 'wb') as f:
                    f.write(response.content)

                return save_path

            else:
                # Handle API errors
                error_msg = f"Eleven Labs API error: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        error_msg += f" - {error_data['detail']}"
                except:
                    error_msg += f" - {response.text}"

                raise Exception(error_msg)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error when calling Eleven Labs API: {str(e)}")
        except Exception as e:
            if "Eleven Labs API error" in str(e):
                raise
            else:
                raise Exception(f"Error generating speech: {str(e)}")

    def get_available_voices(self) -> list:
        """
        Get list of available voices from Eleven Labs

        Returns:
            list: List of voice objects with id, name, and other properties
        """
        url = f"{self.base_url}/voices"

        try:
            response = requests.get(url, headers={"xi-api-key": self.api_key}, timeout=10)

            if response.status_code == 200:
                return response.json().get('voices', [])
            else:
                raise Exception(f"Failed to get voices: {response.status_code}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error when getting voices: {str(e)}")

    def validate_api_key(self) -> bool:
        """
        Validate if the API key is working

        Returns:
            bool: True if API key is valid, False otherwise
        """
        try:
            # Try to get voices as a simple validation
            self.get_available_voices()
            return True
        except:
            return False