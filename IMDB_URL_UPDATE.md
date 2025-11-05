# IMDB URL Update - No Title/Year Required

## Summary

The video creation workflow has been updated to **no longer require movie titles or release years when an IMDB URL is provided**. This makes it easier to create videos by simply using IMDB links.

---

## ✅ What Changed

### Before (Required Both)
```json
{
  "title": "Forrest Gump",
  "release_year": "1994"
}
```

### After (Either/Or)
```json
// Option 1: Just IMDB URL (NEW!)
{
  "imdb_url": "https://www.imdb.com/title/tt0109830/"
}

// Option 2: Title only (still works)
{
  "title": "Forrest Gump"
}

// Option 3: Title + Year (still works)
{
  "title": "Forrest Gump",
  "release_year": "1994"
}

// Option 4: IMDB URL + Title (still works, IMDB URL takes precedence)
{
  "title": "Forrest Gump",
  "imdb_url": "https://www.imdb.com/title/tt0109830/"
}
```

---

## 🎯 Use Cases

### Use Case 1: Scraping IMDB for a Video

If you're scraping IMDB or have IMDB URLs, you can now create videos without extracting titles:

```python
import requests

# Just collected IMDB URLs from scraping
imdb_urls = [
    "https://www.imdb.com/title/tt0109830/",
    "https://www.imdb.com/title/tt0120689/",
    "https://www.imdb.com/title/tt0162222/",
    # ... 6 more URLs
]

# Create manifest using only IMDB URLs
manifest = {
    "first_hint": {
        "caption": "Hard Level\\nHints",
        "movies": [
            {"imdb_url": imdb_urls[0]},
            {"imdb_url": imdb_urls[1]},
            {"imdb_url": imdb_urls[2]}
        ]
    },
    "second_hint": {
        "caption": "Medium Level\\nHints",
        "movies": [
            {"imdb_url": imdb_urls[3]},
            {"imdb_url": imdb_urls[4]},
            {"imdb_url": imdb_urls[5]}
        ]
    },
    "third_hint": {
        "caption": "Easy Level\\nHints",
        "movies": [
            {"imdb_url": imdb_urls[6]},
            {"imdb_url": imdb_urls[7]},
            {"imdb_url": imdb_urls[8]}
        ]
    },
    "answer": {"caption": "Actor Name"}
}

# Create video
response = requests.post('http://localhost:8080/create_tiktok_video', json={
    'manifest': manifest,
    'output_filename': 'video.mp4'
})
```

### Use Case 2: Mix and Match

You can mix IMDB URLs and titles in the same manifest:

```json
{
  "first_hint": {
    "caption": "Hard Level\\nHints",
    "movies": [
      {"imdb_url": "https://www.imdb.com/title/tt0109830/"},
      {"title": "The Green Mile", "release_year": "1999"},
      {"title": "Cast Away"}
    ]
  }
}
```

---

## 🔧 Technical Details

### Validation Logic

**Previous Rule:**
- Movie **must** have a `title` field

**New Rule:**
- Movie **must** have **either** `title` **or** `imdb_url`
- If both provided, `imdb_url` takes precedence for poster lookup

### Poster Download Priority

1. **If `poster_path` is provided**: Use it directly
2. **If `imdb_url` is provided**: Extract IMDB ID and download via OMDB
3. **If only `title` is provided**: Search OMDB by title (and optional year)
4. **If extraction fails**: Fallback to title search (if title provided)
5. **If all fails**: Use placeholder image

### Code Changes

#### [main.py](main.py#L316-L350)
```python
# OLD: Required title
if not isinstance(movie_datum, dict) or "title" not in movie_datum:
    raise ValueError("Each movie data entry must have at least a 'title' key")

# NEW: Requires either title or imdb_url
title = movie_datum.get("title")
imdb_url = movie_datum.get("imdb_url")

if not title and not imdb_url:
    raise ValueError("Each movie data entry must have either a 'title' or 'imdb_url' field")
```

#### [MoviePosterFinder/OMDBClient.py](MoviePosterFinder/OMDBClient.py#L75-L127)
```python
# Added validation to ensure fallback works correctly
if imdb_url:
    imdb_id = self.extract_imdb_id(imdb_url)
    if imdb_id:
        return self.download_movie_poster_by_imdb_id(imdb_id, save_path)
    else:
        # Can only fallback if title is provided
        if not movie_title:
            raise ValueError("Could not extract IMDB ID and no title provided")
        print("Falling back to title/year search")
```

---

## 📝 Updated Examples

### Complete Manifest with IMDB URLs Only

```json
{
  "first_hint": {
    "caption": "Hard Level\\nHints",
    "movies": [
      {"imdb_url": "https://www.imdb.com/title/tt0109830/"},
      {"imdb_url": "https://www.imdb.com/title/tt0120689/"},
      {"imdb_url": "https://www.imdb.com/title/tt0162222/"}
    ]
  },
  "second_hint": {
    "caption": "Medium Level\\nHints",
    "movies": [
      {"imdb_url": "https://www.imdb.com/title/tt0114709/"},
      {"imdb_url": "https://www.imdb.com/title/tt0120815/"},
      {"imdb_url": "https://www.imdb.com/title/tt0114709/"}
    ]
  },
  "third_hint": {
    "caption": "Easy Level\\nHints",
    "movies": [
      {"imdb_url": "https://www.imdb.com/title/tt0096874/"},
      {"imdb_url": "https://www.imdb.com/title/tt0104694/"},
      {"imdb_url": "https://www.imdb.com/title/tt0362227/"}
    ]
  },
  "answer": {
    "caption": "Tom Hanks"
  },
  "background_audio": "assets/background_audio.mp3",
  "background_video": "assets/background_video.mp4"
}
```

### Test File Available

A test manifest using IMDB URLs is available at:
- [test_imdb_only_manifest.json](test_imdb_only_manifest.json)

---

## 🧪 Testing

### Test with IMDB URLs

```bash
# Start server
python launcher.py

# In another terminal, test with IMDB-only manifest
python -c "
import requests
import json

with open('test_imdb_only_manifest.json') as f:
    manifest = json.load(f)

response = requests.post('http://localhost:8080/create_tiktok_video', json={
    'manifest': manifest,
    'output_filename': 'test_imdb_video.mp4'
})

print(response.json())
"
```

---

## 🔄 Backward Compatibility

✅ **Fully backward compatible!**

All existing manifests using `title` and `release_year` will continue to work exactly as before. This change only **adds** the ability to use IMDB URLs without titles.

**Existing manifests work unchanged:**
```json
{
  "movies": [
    {"title": "Movie Name", "release_year": "2020"}
  ]
}
```

**New IMDB-only manifests now work:**
```json
{
  "movies": [
    {"imdb_url": "https://www.imdb.com/title/tt1234567/"}
  ]
}
```

---

## 📚 Updated Documentation

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Updated with IMDB-only examples
- **[test_imdb_only_manifest.json](test_imdb_only_manifest.json)** - Working example

---

## 💡 Benefits

1. **Simpler Integration**: Web scrapers and IMDB integrations don't need to extract titles
2. **More Accurate**: IMDB ID lookup is more precise than title search
3. **Fewer Fields**: Reduces required data in your integration
4. **Future-Proof**: If movie titles change or have variations, IMDB ID remains constant

---

## ⚠️ Error Handling

### Valid Requests
```json
{"imdb_url": "https://www.imdb.com/title/tt0109830/"}  ✅
{"title": "Forrest Gump"}                               ✅
{"title": "Forrest Gump", "release_year": "1994"}      ✅
{"imdb_url": "...", "title": "Forrest Gump"}           ✅
```

### Invalid Requests
```json
{}                                                      ❌ Neither title nor IMDB URL
{"release_year": "1994"}                               ❌ Year alone is not enough
{"imdb_url": "invalid-url"}                            ❌ Invalid IMDB URL (no ID)
```

---

## 🎉 Summary

You can now create videos using **just IMDB URLs** - no need to extract or provide movie titles or release years! This makes integration with IMDB scrapers, databases, or APIs much simpler.

**Old way (still works):**
```json
{"title": "Forrest Gump", "release_year": "1994"}
```

**New way (now works):**
```json
{"imdb_url": "https://www.imdb.com/title/tt0109830/"}
```

Both are valid, and you can mix them in the same manifest! 🚀
