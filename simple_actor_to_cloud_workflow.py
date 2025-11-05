#!/usr/bin/env python3
"""
Simplified Actor-to-Cloud Workflow

This script demonstrates the simplest possible workflow:
1. Provide an actor name
2. Generate manifest (with B2 settings included)
3. Create video and upload to cloud
4. Get back a shareable URL

No manual configuration needed!
"""

import requests
import sys


def create_actor_video_in_cloud(actor_name, base_url="http://localhost:8080"):
    """
    Complete workflow: actor name → video in cloud (simplified version)

    Args:
        actor_name: Name of the actor/actress
        base_url: Base URL of the server

    Returns:
        dict: Result with video URL and details
    """
    print(f"🎬 Creating video for: {actor_name}")
    print("="*60)

    # Step 1: Generate manifest (includes B2 upload settings)
    print("\n📋 Step 1/2: Generating manifest...")
    response = requests.post(f'{base_url}/generate_manifest', json={
        'actor_name': actor_name
    })

    if not response.ok:
        print(f"❌ Failed to generate manifest: {response.status_code}")
        print(response.text)
        return None

    manifest_data = response.json()

    if not manifest_data['success']:
        print(f"❌ {manifest_data['message']}")
        return None

    print(f"✅ Found {manifest_data['total_movies_found']} movies")
    print(f"\n📽️  Selected movies:")
    for i, movie in enumerate(manifest_data['movie_details'][:9], 1):
        print(f"   {i}. {movie['title']} ({movie['release_year']}) - Pop: {movie['popularity']:.1f}")

    # Step 2: Create video using ready-made payload
    print(f"\n🎥 Step 2/2: Creating video and uploading to B2...")
    print("   Note: This may take 2-4 minutes...")

    # ✨ The magic: video_creation_payload already includes:
    # - manifest
    # - upload_to_b2: True
    # - delete_local_after_upload: True
    # - output_filename: "{actor}_video.mp4"

    response = requests.post(
        f'{base_url}/create_tiktok_video',
        json=manifest_data['video_creation_payload'],  # Use ready-made payload!
        timeout=600
    )

    if not response.ok:
        print(f"❌ Failed to create video: {response.status_code}")
        print(response.text)
        return None

    result = response.json()

    if not result['success']:
        print(f"❌ {result['message']}")
        return None

    print(f"\n✅ Video created successfully!")
    print("="*60)
    print(f"📹 Output: {result['output_path']}")

    if result.get('uploaded_to_b2'):
        print(f"\n☁️  Uploaded to Backblaze B2:")
        print(f"   🔗 Download URL: {result['b2_url']}")
        print(f"   📦 File ID: {result['b2_file_id']}")
        print(f"   📝 File Name: {result['b2_file_name']}")
        if result.get('local_deleted'):
            print(f"   🗑️  Local file deleted (saved disk space)")
    else:
        print(f"💾 Saved locally: {result['output_path']}")
        if result.get('upload_to_b2_failed'):
            print(f"⚠️  B2 Upload failed: {result.get('upload_error')}")

    print("="*60)

    return result


if __name__ == "__main__":
    print("\n" + "🎬"*30)
    print("  Simple Actor-to-Cloud Workflow")
    print("🎬"*30 + "\n")

    # Get actor name from command line or use default
    if len(sys.argv) > 1:
        actor_name = " ".join(sys.argv[1:])
    else:
        print("Usage: python simple_actor_to_cloud_workflow.py 'Actor Name'")
        print("\nNo actor provided, using default: Tom Hanks\n")
        actor_name = "Tom Hanks"

    print("⚠️  Requirements:")
    print("  1. Flask server running (python launcher.py)")
    print("  2. TMDB API key set (for actor lookup)")
    print("  3. OMDB API key set (for movie posters)")
    print("  4. B2 credentials set (for cloud upload)")
    print()

    input("Press Enter to continue...")

    try:
        result = create_actor_video_in_cloud(actor_name)

        if result and result.get('uploaded_to_b2'):
            print(f"\n🎉 SUCCESS! Share your video:")
            print(f"   {result['b2_url']}")
        elif result:
            print(f"\n✅ Video created locally:")
            print(f"   {result['output_path']}")
            print(f"\n💡 Tip: Set B2 credentials to enable cloud upload")
        else:
            print(f"\n❌ Workflow failed. Check the errors above.")

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server at http://localhost:8080")
        print("   Make sure the Flask server is running!")
        print("   Run: python launcher.py")
    except KeyboardInterrupt:
        print("\n\n👋 Workflow interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
