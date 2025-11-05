# Actor Name to Video - Complete Automated Workflow

This guide describes the complete automated workflow that takes just an actor's name and produces a finished TikTok video uploaded to the cloud.

---

## 🎯 Overview

**Input:** Actor name (e.g., "Tom Hanks")

**Output:** TikTok video in cloud storage with shareable URL

**Steps:**
1. `/generate_manifest` - Generate manifest from actor name
2. `/create_tiktok_video` - Create video from manifest
3. Automatic B2 upload - Upload to cloud & delete local file

---

## 🚀 Quick Start

### One-Line Command (cURL)

```bash
# Step 1: Generate manifest
curl -X POST http://localhost:8080/generate_manifest \
  -H "Content-Type: application/json" \
  -d '{"actor_name": "Tom Hanks"}' \
  | jq '.manifest' > manifest.json

# Step 2: Create video with B2 upload
curl -X POST http://localhost:8080/create_tiktok_video \
  -H "Content-Type: application/json" \
  -d "{\"manifest\": $(cat manifest.json), \"upload_to_b2\": true, \"delete_local_after_upload\": true}"
```

### Python Script (Recommended)

Use the included test script:

```bash
python test_complete_workflow.py
```

Or create your own:

```python
import requests

# Step 1: Generate manifest from actor name
response = requests.post('http://localhost:8080/generate_manifest', json={
    'actor_name': 'Denzel Washington'
})
manifest = response.json()['manifest']

# Step 2: Create video and upload to B2
response = requests.post('http://localhost:8080/create_tiktok_video', json={
    'manifest': manifest,
    'output_filename': 'denzel_video.mp4',
    'upload_to_b2': True,
    'delete_local_after_upload': True
})

result = response.json()
print(f"✅ Video created and uploaded!")
print(f"🔗 Download URL: {result['b2_url']}")
```

### JavaScript/Web

```javascript
// Complete workflow in one chained request
fetch('/generate_manifest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ actor_name: "Emma Stone" })
})
.then(r => r.json())
.then(data => {
  console.log(`Found ${data.total_movies_found} movies for ${data.actor_name}`);

  // Create video with the generated manifest
  return fetch('/create_tiktok_video', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      manifest: data.manifest,
      output_filename: 'emma_stone_video.mp4',
      upload_to_b2: true,
      delete_local_after_upload: true
    })
  });
})
.then(r => r.json())
.then(result => {
  console.log('✅ Video ready!');
  console.log('🔗 URL:', result.b2_url);
});
```

---

## 📋 Step-by-Step Breakdown

### Step 1: Generate Manifest (`POST /generate_manifest`)

**What it does:**
- Uses TMDB API to search for the actor
- Fetches their top 9 movies sorted by popularity and cast order
- Organizes movies into 3 difficulty levels (3 movies each)
- Creates a complete manifest structure

**Request:**
```json
{
  "actor_name": "Tom Hanks",
  "hint_captions": [
    "Hard Level\nHints",
    "Medium Level\nHints",
    "Easy Level\nHints"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "actor_name": "Tom Hanks",
  "total_movies_found": 171,
  "manifest": {
    "first_hint": {
      "caption": "Hard Level\nHints",
      "movies": [
        { "title": "Forrest Gump", "release_year": "1994" },
        { "title": "Killing Lincoln", "release_year": "2013" },
        { "title": "Who Killed the Electric Car?", "release_year": "2006" }
      ]
    },
    "second_hint": { /* 3 more movies */ },
    "third_hint": { /* 3 more movies */ },
    "answer": { "caption": "Tom Hanks" },
    "background_audio": "assets/background_audio.mp3",
    "background_video": "assets/background_video.mp4"
  }
}
```

**Key Features:**
- ✅ Automatically selects best movies (most popular + high cast billing)
- ✅ No manual movie selection needed
- ✅ Customizable hint captions
- ✅ Returns full movie details for reference

---

### Step 2: Create Video (`POST /create_tiktok_video`)

**What it does:**
- Downloads movie posters via OMDB API
- Downloads actor headshot via TMDB API
- Renders the TikTok video (1080x1920, vertical)
- Uploads to Backblaze B2 (optional)
- Deletes local file (optional)

**Request:**
```json
{
  "manifest": { /* manifest from step 1 */ },
  "output_filename": "tom_hanks_video.mp4",
  "upload_to_b2": true,
  "delete_local_after_upload": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "TikTok video created and uploaded to B2! Local file deleted.",
  "output_path": "./tom_hanks_video.mp4",
  "uploaded_to_b2": true,
  "b2_url": "https://f005.backblazeb2.com/file/my-bucket/tom_hanks_video.mp4",
  "b2_file_id": "4_z123...",
  "b2_file_name": "tom_hanks_video.mp4",
  "local_deleted": true
}
```

**Key Features:**
- ✅ Automatic resource fetching (posters, headshots)
- ✅ Professional video rendering
- ✅ Cloud upload with shareable URL
- ✅ Local cleanup to save disk space

---

## 🎬 Complete Workflow Example

### Full Python Implementation

```python
#!/usr/bin/env python3
"""
Complete actor-to-video workflow with B2 upload
"""
import requests
import json

BASE_URL = "http://localhost:8080"

def create_video_from_actor(actor_name, upload_to_cloud=True):
    """
    Complete workflow: actor name → video in cloud

    Args:
        actor_name: Name of actor/actress
        upload_to_cloud: Whether to upload to B2 and delete local file

    Returns:
        dict: Result with video URL and details
    """
    print(f"🎬 Creating video for: {actor_name}")

    # Step 1: Generate manifest
    print("📋 Step 1/2: Generating manifest...")
    response = requests.post(f'{BASE_URL}/generate_manifest', json={
        'actor_name': actor_name,
        'hint_captions': [
            "Cinephile\nLevel\nHints",
            "Movie Buff\nLevel\nHints",
            "Everyone\nKnows\nThese"
        ]
    })

    if not response.ok:
        raise Exception(f"Failed to generate manifest: {response.text}")

    manifest_data = response.json()
    manifest = manifest_data['manifest']

    print(f"✅ Found {manifest_data['total_movies_found']} movies")
    print(f"   Selected 9 for video:")
    for i, movie in enumerate(manifest_data['movie_details'][:9], 1):
        print(f"   {i}. {movie['title']} ({movie['release_year']})")

    # Step 2: Create video
    print(f"\n🎥 Step 2/2: Creating video...")
    output_filename = f"{actor_name.lower().replace(' ', '_')}_video.mp4"

    response = requests.post(f'{BASE_URL}/create_tiktok_video', json={
        'manifest': manifest,
        'output_filename': output_filename,
        'upload_to_b2': upload_to_cloud,
        'delete_local_after_upload': upload_to_cloud
    }, timeout=600)

    if not response.ok:
        raise Exception(f"Failed to create video: {response.text}")

    result = response.json()

    print(f"\n✅ Video created successfully!")

    if result.get('uploaded_to_b2'):
        print(f"☁️  Uploaded to Backblaze B2")
        print(f"🔗 Download URL: {result['b2_url']}")
        if result.get('local_deleted'):
            print(f"🗑️  Local file deleted (saved disk space)")
    else:
        print(f"💾 Saved locally: {result['output_path']}")

    return result

# Example usage
if __name__ == "__main__":
    actors = ["Tom Hanks", "Meryl Streep", "Denzel Washington"]

    for actor in actors:
        try:
            result = create_video_from_actor(actor, upload_to_cloud=True)
            print(f"\n{'='*60}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
```

---

## 🎨 Customization Options

### Custom Hint Captions

```python
response = requests.post('/generate_manifest', json={
    'actor_name': 'Leonardo DiCaprio',
    'hint_captions': [
        "Film School\nGraduate\nLevel",
        "Weekend\nMovie Night\nLevel",
        "Netflix & Chill\nLevel"
    ]
})
```

### Custom Background Media

```python
manifest['background_audio'] = 'path/to/your/audio.mp3'
manifest['background_video'] = 'path/to/your/video.mp4'

response = requests.post('/create_tiktok_video', json={
    'manifest': manifest,
    ...
})
```

### No Cloud Upload (Keep Local)

```python
response = requests.post('/create_tiktok_video', json={
    'manifest': manifest,
    'output_filename': 'video.mp4',
    'upload_to_b2': False  # Keep file locally
})
```

---

## ⚙️ Configuration

### Required Environment Variables

```bash
# TMDB API (for actor movie lookup)
export GTA_TMDB_API_KEY="your_tmdb_key"

# OMDB API (for movie poster downloads)
export GTA_OMDB_API_KEY="your_omdb_key"

# Backblaze B2 (optional, for cloud upload)
export B2_APPLICATION_KEY_ID="your_b2_key_id"
export B2_APPLICATION_KEY="your_b2_key"
export B2_BUCKET_NAME="your_bucket_name"
```

### API Key Alternatives

You can also pass API keys in requests:

```python
response = requests.post('/generate_manifest', json={
    'actor_name': 'Actor Name',
    'tmdb_api_key': 'your_tmdb_key',
    'omdb_api_key': 'your_omdb_key'
})
```

---

## 📊 Performance

**Typical Workflow Timing:**

| Step | Duration | Notes |
|------|----------|-------|
| Generate Manifest | 2-5 seconds | TMDB API calls |
| Download Posters | 10-30 seconds | 9 movie posters via OMDB |
| Download Headshot | 2-5 seconds | 1 actor image via TMDB |
| Render Video | 60-180 seconds | Video processing (MoviePy) |
| Upload to B2 | 10-30 seconds | ~15MB upload |
| **Total** | **2-4 minutes** | End-to-end |

**Optimization Tips:**
- Use environment variables for API keys (faster than passing in requests)
- Have background video/audio pre-downloaded in assets folder
- B2 upload is concurrent with video finalization

---

## 🐛 Troubleshooting

### "Actor not found"
- Check spelling of actor name
- Try variations (e.g., "Tom Hanks" vs "Thomas Hanks")
- Ensure TMDB API key is valid

### "Not enough movies found"
- Some actors may not have 9 qualifying movies
- Try a more prolific actor
- Check that the actor has movie credits (not just TV)

### Video creation fails
- Check OMDB API key is valid
- Ensure background assets exist
- Check disk space (videos are ~15MB)

### B2 upload fails
- Verify B2 credentials are set
- Check bucket exists and is accessible
- Ensure network connectivity

---

## 📚 Related Documentation

- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Complete API reference
- [B2_SETUP_GUIDE.md](B2_SETUP_GUIDE.md) - Backblaze B2 setup
- [test_complete_workflow.py](test_complete_workflow.py) - Working example script

---

## 🎉 Summary

You can now create a complete TikTok video from just an actor's name with a single workflow:

1. **Input**: Actor name
2. **Processing**: Automatic movie selection, poster downloads, video rendering
3. **Output**: Cloud-hosted video with shareable URL

**No manual work required!** 🚀
