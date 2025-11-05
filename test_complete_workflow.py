#!/usr/bin/env python3
"""
Test the complete workflow:
1. Generate manifest from actor name
2. Use manifest to create video
3. Optionally upload to B2
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8080"
ACTOR_NAME = "Tom Hanks"

# API Keys (set these in your .env or provide here)
OMDB_API_KEY = ""  # Optional: leave empty to use env var
TMDB_API_KEY = ""  # Optional: leave empty to use env var

# B2 Configuration (set these in your .env or provide here)
B2_APPLICATION_KEY_ID = ""  # Optional: leave empty to use env var
B2_APPLICATION_KEY = ""  # Optional: leave empty to use env var
B2_BUCKET_NAME = ""  # Optional: leave empty to use env var

def step1_generate_manifest():
    """Step 1: Generate manifest from actor name"""
    print("="*60)
    print(f"STEP 1: Generating manifest for {ACTOR_NAME}")
    print("="*60)

    payload = {
        "actor_name": ACTOR_NAME,
        "hint_captions": [
            "Hardest\nLevel\nHints",
            "Medium\nLevel\nHints",
            "Easiest\nLevel\nHints"
        ]
    }

    # Add API keys if provided
    if TMDB_API_KEY:
        payload["tmdb_api_key"] = TMDB_API_KEY
    if OMDB_API_KEY:
        payload["omdb_api_key"] = OMDB_API_KEY

    response = requests.post(f"{BASE_URL}/generate_manifest", json=payload)

    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

    data = response.json()

    if not data['success']:
        print(f"❌ Failed: {data['message']}")
        return None

    print(f"✅ Manifest generated successfully!")
    print(f"   Actor: {data['actor_name']}")
    print(f"   Total movies in database: {data['total_movies_found']}")
    print(f"\n📽️  Selected Movies:")

    for i, movie in enumerate(data['movie_details'][:9], 1):
        print(f"   {i}. {movie['title']} ({movie['release_year']}) - Popularity: {movie['popularity']:.1f}")

    return data['manifest']


def step2_create_video(manifest, upload_to_b2=False):
    """Step 2: Create video from manifest"""
    print("\n" + "="*60)
    print(f"STEP 2: Creating TikTok video")
    if upload_to_b2:
        print("        (with B2 upload enabled)")
    print("="*60)

    payload = {
        "manifest": manifest,
        "output_filename": f"{ACTOR_NAME.lower().replace(' ', '_')}_video.mp4",
        "output_path": ".",
        "upload_to_b2": upload_to_b2,
        "delete_local_after_upload": upload_to_b2
    }

    # Add B2 credentials if provided and upload enabled
    if upload_to_b2:
        if B2_APPLICATION_KEY_ID:
            payload["b2_application_key_id"] = B2_APPLICATION_KEY_ID
        if B2_APPLICATION_KEY:
            payload["b2_application_key"] = B2_APPLICATION_KEY
        if B2_BUCKET_NAME:
            payload["b2_bucket_name"] = B2_BUCKET_NAME

    print("\n⏳ Creating video (this may take a few minutes)...")
    print("   Note: The server will download movie posters and actor headshot")
    print("   Then it will render the video...")

    start_time = time.time()

    # This request may take several minutes
    response = requests.post(
        f"{BASE_URL}/create_tiktok_video",
        json=payload,
        timeout=600  # 10 minute timeout
    )

    elapsed_time = time.time() - start_time

    if response.status_code != 200:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        return None

    data = response.json()

    if not data['success']:
        print(f"\n❌ Failed: {data['message']}")
        return None

    print(f"\n✅ Video created successfully! (took {elapsed_time:.1f} seconds)")
    print(f"   Local path: {data['output_path']}")

    if data.get('uploaded_to_b2'):
        print(f"\n☁️  Uploaded to Backblaze B2:")
        print(f"   File ID: {data['b2_file_id']}")
        print(f"   File Name: {data['b2_file_name']}")
        print(f"   Download URL: {data['b2_url']}")
        print(f"   Local file deleted: {data['local_deleted']}")
    elif data.get('upload_to_b2_failed'):
        print(f"\n⚠️  B2 Upload failed: {data['upload_error']}")

    return data


def main():
    """Run the complete workflow"""
    print("\n" + "🎬"*30)
    print("  TikTok Creator - Complete Workflow Test")
    print("🎬"*30 + "\n")

    # Step 1: Generate manifest
    manifest = step1_generate_manifest()
    if not manifest:
        return

    # Optional: Save manifest to file for inspection
    with open(f"{ACTOR_NAME.lower().replace(' ', '_')}_manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"\n💾 Manifest saved to: {ACTOR_NAME.lower().replace(' ', '_')}_manifest.json")

    # Step 2: Create video
    # Set upload_to_b2=True to enable cloud upload
    result = step2_create_video(manifest, upload_to_b2=False)

    if result:
        print("\n" + "="*60)
        print("🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nNext steps:")
        print("  1. Watch the video to verify it looks good")
        print("  2. Set upload_to_b2=True in this script to enable cloud upload")
        print("  3. Configure B2 credentials in .env or this script")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ WORKFLOW FAILED")
        print("="*60)


if __name__ == "__main__":
    print("\n⚠️  IMPORTANT: Make sure the Flask server is running!")
    print("   Start it with: python launcher.py")
    print()

    input("Press Enter to continue...")

    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server at http://localhost:8080")
        print("   Make sure the Flask server is running!")
    except KeyboardInterrupt:
        print("\n\n👋 Workflow interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
