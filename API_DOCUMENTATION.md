# TikTok Creator - Server API Documentation

This document describes the HTTP API endpoints provided by the TikTok Creator Flask server.

## Base URL

```
http://localhost:8080
```

## Server Files

- **Primary Server**: `launcher.py` - Production server with browser auto-launch
- **Development Server**: `web_gui/app.py` - Development server with debug mode

---

## Endpoints

### 1. Static File Endpoints

#### GET `/`
Serves the main HTML page for the web interface.

**Response:**
- **Content-Type**: `text/html`
- **Body**: HTML content from `web_gui/index.html`

---

#### GET `/style.css`
Serves the CSS stylesheet.

**Response:**
- **Content-Type**: `text/css`
- **Body**: CSS content from `web_gui/style.css`

---

#### GET `/script.js`
Serves the JavaScript file.

**Response:**
- **Content-Type**: `application/javascript`
- **Body**: JavaScript content from `web_gui/script.js`

---

### 2. API Endpoints

#### POST `/create_tiktok_video`

Creates a TikTok video from the provided manifest data.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "manifest": {
    "first_hint": {
      "caption": "string",
      "movies": [
        {
          "title": "string",
          "release_year": "string (optional)",
          "poster_path": "string (optional)",
          "imdb_url": "string (optional)"
        }
      ]
    },
    "second_hint": {
      "caption": "string",
      "movies": [
        {
          "title": "string",
          "release_year": "string (optional)",
          "poster_path": "string (optional)",
          "imdb_url": "string (optional)"
        }
      ]
    },
    "third_hint": {
      "caption": "string",
      "movies": [
        {
          "title": "string",
          "release_year": "string (optional)",
          "poster_path": "string (optional)",
          "imdb_url": "string (optional)"
        }
      ]
    },
    "answer": {
      "caption": "string",
      "image_path": "string (optional)"
    },
    "background_audio": "string (optional, defaults to 'assets/background_audio.mp3')",
    "background_video": "string (optional, defaults to 'assets/background_video.mp4')",
    "omdb_api_key": "string (optional, can also use GTA_OMDB_API_KEY env var)",
    "tmdb_api_key": "string (optional, can also use GTA_TMDB_API_KEY env var)"
  },
  "output_path": "string (optional, defaults to '.')",
  "output_filename": "string (optional, defaults to 'output_video.mp4')",
  "upload_to_b2": "boolean (optional, defaults to false) - Upload video to Backblaze B2",
  "delete_local_after_upload": "boolean (optional, defaults to true) - Delete local file after B2 upload",
  "b2_application_key_id": "string (optional, can also use B2_APPLICATION_KEY_ID env var)",
  "b2_application_key": "string (optional, can also use B2_APPLICATION_KEY env var)",
  "b2_bucket_name": "string (optional, can also use B2_BUCKET_NAME env var)"
}
```

**Request Body Field Descriptions:**

- **manifest** (required): The video configuration object
  - **first_hint**, **second_hint**, **third_hint** (required): Three hint sections
    - **caption**: Text to display for this hint level
    - **movies**: Array of exactly 3 movie objects (each movie must have either `title` or `imdb_url`)
      - **title**: Movie title (required if `imdb_url` not provided, optional if `imdb_url` is provided)
      - **release_year**: Release year for more accurate poster lookup (optional, not needed if `imdb_url` provided)
      - **poster_path**: Path to custom poster image (optional, will auto-fetch if not provided)
      - **imdb_url**: IMDB URL (required if `title` not provided, can be used instead of title/year for poster lookup)
  - **answer** (required): The answer section
    - **caption**: Actor/actress name
    - **image_path**: Path to actor headshot (optional, will auto-fetch from TMDB if not provided)
  - **background_audio**: Path to background audio file (optional)
  - **background_video**: Path to background video file (optional)
  - **omdb_api_key**: OMDB API key for movie poster downloads (optional if env var set)
  - **tmdb_api_key**: TMDB API key for actor headshot downloads (optional if env var set)
- **output_path**: Directory where the video will be saved (optional, defaults to current directory)
- **output_filename**: Name of the output video file (optional, defaults to 'output_video.mp4')
- **upload_to_b2**: Enable automatic upload to Backblaze B2 cloud storage (optional, defaults to false)
- **delete_local_after_upload**: Delete local video file after successful B2 upload (optional, defaults to true)
- **b2_application_key_id**: Backblaze B2 application key ID (optional if B2_APPLICATION_KEY_ID env var set)
- **b2_application_key**: Backblaze B2 application key (optional if B2_APPLICATION_KEY env var set)
- **b2_bucket_name**: Backblaze B2 bucket name (optional if B2_BUCKET_NAME env var set)

**Success Response (200) - Without B2 Upload:**
```json
{
  "success": true,
  "message": "TikTok video created successfully!",
  "output_path": "/full/path/to/output_video.mp4",
  "output": "Video saved to: /full/path/to/output_video.mp4"
}
```

**Success Response (200) - With B2 Upload:**
```json
{
  "success": true,
  "message": "TikTok video created and uploaded to B2! Local file deleted.",
  "output_path": "/full/path/to/output_video.mp4",
  "output": "Video saved to: /full/path/to/output_video.mp4",
  "uploaded_to_b2": true,
  "b2_url": "https://f005.backblazeb2.com/file/my-bucket/output_video.mp4",
  "b2_file_id": "4_z123456789abcdef_f987654321fedcba_d20231104_m123456_c005_v0001234_t0012",
  "b2_file_name": "output_video.mp4",
  "local_deleted": true
}
```

**Success Response (200) - With B2 Upload Failure:**
```json
{
  "success": true,
  "message": "TikTok video created successfully!",
  "output_path": "/full/path/to/output_video.mp4",
  "output": "Video saved to: /full/path/to/output_video.mp4",
  "upload_to_b2_failed": true,
  "upload_error": "B2 credentials must be provided"
}
```

**Error Response - Missing Manifest (400):**
```json
{
  "success": false,
  "message": "No manifest data provided"
}
```

**Error Response - Processing Error (500):**
```json
{
  "success": false,
  "message": "Error creating TikTok video: [error message]",
  "errors": "[detailed traceback]"
}
```

**Example Request (Basic):**
```javascript
fetch('/create_tiktok_video', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    manifest: {
      first_hint: {
        caption: "Hard Level\\nHints",
        movies: [
          {
            title: "Forrest Gump",
            release_year: "1994"
          },
          {
            title: "The Green Mile"
          },
          {
            imdb_url: "https://www.imdb.com/title/tt0120689/"
          }
        ]
      },
      second_hint: {
        caption: "Medium Level\\nHints",
        movies: [
          { title: "Cast Away", release_year: "2000" },
          { title: "Toy Story" },
          { title: "Saving Private Ryan" }
        ]
      },
      third_hint: {
        caption: "Easy Level\\nHints",
        movies: [
          { title: "Big", release_year: "1988" },
          { title: "A League of Their Own" },
          { title: "The Terminal" }
        ]
      },
      answer: {
        caption: "Tom Hanks"
      },
      background_audio: "assets/background_audio.mp3",
      background_video: "assets/background_video.mp4",
      omdb_api_key: "your_omdb_key_here",
      tmdb_api_key: "your_tmdb_key_here"
    },
    output_path: ".",
    output_filename: "tom_hanks_video.mp4"
  })
})
```

**Example Request (Using IMDB URLs Only - No Titles Required):**
```javascript
fetch('/create_tiktok_video', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    manifest: {
      first_hint: {
        caption: "Hard Level\\nHints",
        movies: [
          {
            imdb_url: "https://www.imdb.com/title/tt0109830/"  // Forrest Gump
          },
          {
            imdb_url: "https://www.imdb.com/title/tt0120689/"  // The Green Mile
          },
          {
            imdb_url: "https://www.imdb.com/title/tt0162222/"  // Cast Away
          }
        ]
      },
      second_hint: {
        caption: "Medium Level\\nHints",
        movies: [
          { imdb_url: "https://www.imdb.com/title/tt0114709/" },  // Toy Story
          { imdb_url: "https://www.imdb.com/title/tt0120815/" },  // Saving Private Ryan
          { imdb_url: "https://www.imdb.com/title/tt0114709/" }   // Toy Story 2
        ]
      },
      third_hint: {
        caption: "Easy Level\\nHints",
        movies: [
          { imdb_url: "https://www.imdb.com/title/tt0096874/" },  // Big
          { imdb_url: "https://www.imdb.com/title/tt0104694/" },  // A League of Their Own
          { imdb_url: "https://www.imdb.com/title/tt0362227/" }   // The Terminal
        ]
      },
      answer: {
        caption: "Tom Hanks"
      }
    },
    output_filename: "tom_hanks_imdb_video.mp4"
  })
})
```

**Example Request (With Backblaze B2 Upload):**
```javascript
fetch('/create_tiktok_video', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    manifest: {
      first_hint: { /* ... */ },
      second_hint: { /* ... */ },
      third_hint: { /* ... */ },
      answer: {
        caption: "Tom Hanks"
      },
      omdb_api_key: "your_omdb_key_here",
      tmdb_api_key: "your_tmdb_key_here"
    },
    output_path: ".",
    output_filename: "tom_hanks_video.mp4",
    // Backblaze B2 configuration
    upload_to_b2: true,
    delete_local_after_upload: true,
    b2_application_key_id: "your_b2_key_id",
    b2_application_key: "your_b2_key",
    b2_bucket_name: "my-tiktok-videos"
  })
})
.then(response => response.json())
.then(data => {
  if (data.uploaded_to_b2) {
    console.log('Video uploaded to B2!');
    console.log('Download URL:', data.b2_url);
    console.log('Local file deleted:', data.local_deleted);
  }
})
```

---

#### POST `/generate_manifest`

Generates a complete manifest from an actor's name using the ActorMovieRecommender. Returns a manifest structure that can be directly sent to the `/create_tiktok_video` endpoint.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "actor_name": "string (required)",
  "hint_captions": ["string", "string", "string"] (optional),
  "background_audio": "string (optional)",
  "background_video": "string (optional)",
  "tmdb_api_key": "string (optional)",
  "omdb_api_key": "string (optional)"
}
```

**Request Body Field Descriptions:**
- **actor_name** (required): The name of the actor/actress to generate the manifest for
- **hint_captions** (optional): Array of 3 caption strings for the hint levels (defaults to "Hard/Medium/Easy Level Hints")
- **background_audio** (optional): Path to background audio file (defaults to 'assets/background_audio.mp3')
- **background_video** (optional): Path to background video file (defaults to 'assets/background_video.mp4')
- **tmdb_api_key** (optional): TMDB API key for fetching movies (can use env var)
- **omdb_api_key** (optional): OMDB API key for poster downloads (can use env var)
- **b2_application_key_id** (optional): Backblaze B2 credentials to include in response
- **b2_application_key** (optional): Backblaze B2 credentials to include in response
- **b2_bucket_name** (optional): Backblaze B2 bucket name to include in response

**Success Response (200):**
```json
{
  "success": true,
  "message": "Manifest generated successfully for Tom Hanks",
  "actor_name": "Tom Hanks",
  "total_movies_found": 171,
  "manifest": {
    "first_hint": {
      "caption": "Hard Level\nHints",
      "movies": [
        {
          "title": "Forrest Gump",
          "release_year": "1994"
        },
        {
          "title": "Killing Lincoln",
          "release_year": "2013"
        },
        {
          "title": "Who Killed the Electric Car?",
          "release_year": "2006"
        }
      ]
    },
    "second_hint": {
      "caption": "Medium Level\nHints",
      "movies": [ /* 3 more movies */ ]
    },
    "third_hint": {
      "caption": "Easy Level\nHints",
      "movies": [ /* 3 more movies */ ]
    },
    "answer": {
      "caption": "Tom Hanks"
    },
    "background_audio": "assets/background_audio.mp3",
    "background_video": "assets/background_video.mp4",
    "omdb_api_key": "your_key_if_provided",
    "tmdb_api_key": "your_key_if_provided"
  },
  "movie_details": [
    {
      "title": "Forrest Gump",
      "release_year": "1994",
      "character": "Forrest Gump",
      "cast_order": 0,
      "popularity": 81.0362,
      "vote_average": 8.464,
      "movie_id": 13,
      "overview": "A man with a low IQ..."
    }
    /* ... 8 more movies with full details */
  ],
  "video_creation_payload": {
    "manifest": { /* same as above */ },
    "upload_to_b2": true,
    "delete_local_after_upload": true,
    "output_filename": "tom_hanks_video.mp4"
  }
}
```

**Error Response - Actor Not Found (404):**
```json
{
  "success": false,
  "message": "Actor not found: Unknown Actor"
}
```

**Error Response - Not Enough Movies (400):**
```json
{
  "success": false,
  "message": "Not enough movies found for Actor Name. Found 5, need 9.",
  "movies_found": 5
}
```

**Error Response - Processing Error (500):**
```json
{
  "success": false,
  "message": "Error generating manifest: [error message]",
  "errors": "[detailed traceback]"
}
```

**Example Request (Simple - Using video_creation_payload):**
```javascript
// Step 1: Generate manifest from actor name
fetch('/generate_manifest', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    actor_name: "Denzel Washington"
  })
})
.then(response => response.json())
.then(data => {
  console.log('Manifest generated:', data.manifest);

  // Step 2: Use the ready-made video_creation_payload
  return fetch('/create_tiktok_video', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data.video_creation_payload)  // ✨ Already includes upload_to_b2 and delete_local_after_upload!
  });
})
.then(response => response.json())
.then(data => {
  console.log('Video created:', data.b2_url);
});
```

**Example Request (Custom Configuration):**
```javascript
// Step 1: Generate manifest from actor name
fetch('/generate_manifest', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    actor_name: "Denzel Washington",
    hint_captions: [
      "Cinephile\nLevel\nHints",
      "Casual\nViewer\nHints",
      "Everyone\nKnows\nThese"
    ]
  })
})
.then(response => response.json())
.then(data => {
  console.log('Manifest generated:', data.manifest);

  // Step 2: Use the manifest to create a video (manual configuration)
  return fetch('/create_tiktok_video', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      manifest: data.manifest,
      output_filename: "denzel_video.mp4",
      upload_to_b2: true,
      delete_local_after_upload: true
    })
  });
})
.then(response => response.json())
.then(data => {
  console.log('Video created:', data.b2_url);
});
```

**Complete Workflow Example (Python - Simple):**
```python
import requests

# Step 1: Generate manifest
response = requests.post('http://localhost:8080/generate_manifest', json={
    'actor_name': 'Tom Hanks'
})
manifest_data = response.json()

# Step 2: Create video with ready-made payload (already has upload_to_b2=True)
response = requests.post('http://localhost:8080/create_tiktok_video',
    json=manifest_data['video_creation_payload']  # ✨ Use ready-made payload
)
result = response.json()

print(f"Video URL: {result['b2_url']}")
```

**Complete Workflow Example (Python - Custom):**
```python
import requests

# Step 1: Generate manifest
response = requests.post('http://localhost:8080/generate_manifest', json={
    'actor_name': 'Tom Hanks'
})
manifest_data = response.json()
manifest = manifest_data['manifest']

# Step 2: Create video with custom configuration
response = requests.post('http://localhost:8080/create_tiktok_video', json={
    'manifest': manifest,
    'output_filename': 'tom_hanks_video.mp4',
    'upload_to_b2': True,
    'delete_local_after_upload': True
})
result = response.json()

print(f"Video URL: {result['b2_url']}")
```

---

#### POST `/save_manifest`

*(Only available in web_gui/app.py - development server)*

Saves the manifest data to `input/manifest.json` on the server.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "first_hint": { ... },
  "second_hint": { ... },
  "third_hint": { ... },
  "answer": { ... },
  "background_audio": "string",
  "background_video": "string"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Manifest saved to /path/to/input/manifest.json",
  "path": "/path/to/input/manifest.json"
}
```

**Error Response (500):**
```json
{
  "success": false,
  "message": "Error saving manifest: [error message]"
}
```

---

#### POST `/shutdown`

Gracefully shuts down the Flask server.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Server shutting down..."
}
```

**Error Response (200):**
```json
{
  "success": false,
  "message": "Error during shutdown: [error message]"
}
```

**Example Request:**
```javascript
fetch('/shutdown', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({})
})
```

---

## Server Behavior

### Automatic Resource Fetching

When creating a video, the server automatically fetches missing resources:

1. **Movie Posters**: If `poster_path` is not provided for a movie, the server uses the OMDB API to download the poster based on:
   - Movie title + release year (if provided)
   - OR IMDB URL (if provided)

2. **Actor Headshots**: If `image_path` is not provided in the answer section, the server uses the TMDB API to download the actor's headshot based on the actor name.

### API Keys

API keys can be provided in two ways (manifest keys take precedence):
1. In the manifest: `omdb_api_key` and `tmdb_api_key` fields
2. As environment variables: `GTA_OMDB_API_KEY` and `GTA_TMDB_API_KEY`

### File Paths

All file paths in the manifest can be:
- Absolute paths
- Relative paths (resolved from the project root directory)

### Video Output

- Default output directory: Current working directory (`.`)
- Default output filename: `output_video.mp4`
- Output directory is created automatically if it doesn't exist
- Video format: MP4 (H.264 codec)
- Video dimensions: 1080x1920 (vertical/portrait for TikTok)
- Frame rate: 30 fps

---

## Error Handling

All endpoints return JSON responses with the following error structure:

```json
{
  "success": false,
  "message": "Human-readable error message",
  "errors": "Detailed error information (optional, for debugging)"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (missing required data)
- `500`: Internal Server Error (processing failed)

---

## Running the Server

### Production Mode (launcher.py)
```bash
python launcher.py
```
- Runs on `http://0.0.0.0:8080`
- Automatically opens browser
- Use `--no-browser` flag to prevent auto-launch

### Development Mode (web_gui/app.py)
```bash
cd web_gui
python app.py
```
- Runs on `http://0.0.0.0:8080`
- Debug mode enabled
- Includes `/save_manifest` endpoint

---

## Notes

- The server creates temporary files during video processing that are automatically cleaned up
- Video creation is a synchronous operation (request blocks until video is complete)
- Large videos may take several minutes to process
- The server uses the main video creation logic from `main.py`
