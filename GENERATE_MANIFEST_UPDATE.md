# Generate Manifest Update - B2 Upload Included

## Summary

The `/generate_manifest` endpoint has been updated to include a **ready-to-use `video_creation_payload`** with `upload_to_b2` and `delete_local_after_upload` fields set to `true`.

This makes the workflow even simpler - you can now use the response directly without manually adding B2 configuration!

---

## ✅ What Changed

### Before (Manual Configuration Required)

```python
# Step 1: Generate manifest
response = requests.post('/generate_manifest', json={'actor_name': 'Tom Hanks'})
manifest = response.json()['manifest']

# Step 2: Manually configure video creation
response = requests.post('/create_tiktok_video', json={
    'manifest': manifest,
    'upload_to_b2': True,              # ❌ Had to add this
    'delete_local_after_upload': True, # ❌ Had to add this
    'output_filename': 'tom_hanks_video.mp4'  # ❌ Had to add this
})
```

### After (Automatic Configuration)

```python
# Step 1: Generate manifest
response = requests.post('/generate_manifest', json={'actor_name': 'Tom Hanks'})
data = response.json()

# Step 2: Use ready-made payload
response = requests.post('/create_tiktok_video',
    json=data['video_creation_payload']  # ✨ Already configured!
)
```

---

## 📦 New Response Structure

The `/generate_manifest` endpoint now returns an additional field: `video_creation_payload`

### Response Example

```json
{
  "success": true,
  "actor_name": "Tom Hanks",
  "total_movies_found": 171,
  "manifest": {
    "first_hint": { /* ... */ },
    "second_hint": { /* ... */ },
    "third_hint": { /* ... */ },
    "answer": { "caption": "Tom Hanks" }
  },
  "movie_details": [ /* array of 9 movies */ ],
  "video_creation_payload": {
    "manifest": { /* same manifest as above */ },
    "upload_to_b2": true,
    "delete_local_after_upload": true,
    "output_filename": "tom_hanks_video.mp4"
  }
}
```

### What's Included in `video_creation_payload`

- ✅ `manifest` - Complete video manifest
- ✅ `upload_to_b2: true` - Automatic cloud upload enabled
- ✅ `delete_local_after_upload: true` - Automatic local cleanup
- ✅ `output_filename` - Auto-generated from actor name
- ✅ B2 credentials (if provided in the request)

---

## 🚀 Usage Examples

### JavaScript (Simplified)

```javascript
// Old way (2 steps with manual config)
fetch('/generate_manifest', {
  method: 'POST',
  body: JSON.stringify({ actor_name: "Tom Hanks" })
})
.then(r => r.json())
.then(data => {
  return fetch('/create_tiktok_video', {
    method: 'POST',
    body: JSON.stringify({
      manifest: data.manifest,
      upload_to_b2: true,  // Manual config
      delete_local_after_upload: true  // Manual config
    })
  });
})

// New way (2 steps, automatic config)
fetch('/generate_manifest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ actor_name: "Tom Hanks" })
})
.then(r => r.json())
.then(data => {
  return fetch('/create_tiktok_video', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data.video_creation_payload)  // ✨ Done!
  });
})
.then(r => r.json())
.then(result => console.log('Video URL:', result.b2_url));
```

### Python (Simplified)

```python
import requests

# Step 1: Generate manifest
response = requests.post('http://localhost:8080/generate_manifest', json={
    'actor_name': 'Meryl Streep'
})
data = response.json()

# Step 2: Create video (one line!)
result = requests.post('http://localhost:8080/create_tiktok_video',
    json=data['video_creation_payload']
).json()

print(f"Video URL: {result['b2_url']}")
```

### Complete Example Script

A new simplified example script is available:
- [simple_actor_to_cloud_workflow.py](simple_actor_to_cloud_workflow.py)

Run it:
```bash
python simple_actor_to_cloud_workflow.py "Leonardo DiCaprio"
```

---

## 🎨 Customization Options

### Option 1: Use Ready-Made Payload (Simplest)

```python
data = requests.post('/generate_manifest', json={'actor_name': 'Actor'}).json()
result = requests.post('/create_tiktok_video', json=data['video_creation_payload']).json()
```

**Includes:**
- `upload_to_b2: true`
- `delete_local_after_upload: true`
- `output_filename: "{actor}_video.mp4"`

### Option 2: Customize the Payload

```python
data = requests.post('/generate_manifest', json={'actor_name': 'Actor'}).json()

# Modify the payload
payload = data['video_creation_payload']
payload['output_filename'] = 'my_custom_name.mp4'
payload['delete_local_after_upload'] = False  # Keep local copy

result = requests.post('/create_tiktok_video', json=payload).json()
```

### Option 3: Build Your Own (Full Control)

```python
data = requests.post('/generate_manifest', json={'actor_name': 'Actor'}).json()

# Use only the manifest, configure everything else manually
result = requests.post('/create_tiktok_video', json={
    'manifest': data['manifest'],
    'upload_to_b2': False,  # Keep local only
    'output_filename': 'local_video.mp4',
    'output_path': '/custom/path'
}).json()
```

---

## 🔧 Technical Details

### Changes to Both Servers

Updated files:
- [launcher.py](launcher.py) - Production server
- [web_gui/app.py](web_gui/app.py) - Development server

### Code Changes

```python
# Create complete payload ready for /create_tiktok_video endpoint
video_creation_payload = {
    'manifest': manifest,
    'upload_to_b2': True,
    'delete_local_after_upload': True,
    'output_filename': f"{actor_name.lower().replace(' ', '_')}_video.mp4"
}

# Add B2 credentials to payload if provided
if 'b2_application_key_id' in data:
    video_creation_payload['b2_application_key_id'] = data['b2_application_key_id']
if 'b2_application_key' in data:
    video_creation_payload['b2_application_key'] = data['b2_application_key']
if 'b2_bucket_name' in data:
    video_creation_payload['b2_bucket_name'] = data['b2_bucket_name']

return jsonify({
    # ... existing fields ...
    'video_creation_payload': video_creation_payload  # NEW!
})
```

### Passing B2 Credentials

If you want to override environment variables, pass B2 credentials in the `/generate_manifest` request:

```python
response = requests.post('/generate_manifest', json={
    'actor_name': 'Tom Hanks',
    'b2_application_key_id': 'your_key_id',
    'b2_application_key': 'your_key',
    'b2_bucket_name': 'your_bucket'
})

# The video_creation_payload will include these credentials
data = response.json()
# data['video_creation_payload'] contains the B2 credentials
```

---

## 🔄 Backward Compatibility

✅ **Fully backward compatible!**

The `manifest` field is still returned separately, so existing code continues to work:

```python
# This still works exactly as before
data = requests.post('/generate_manifest', json={'actor_name': 'Actor'}).json()
manifest = data['manifest']  # ✅ Still available

response = requests.post('/create_tiktok_video', json={
    'manifest': manifest,
    'upload_to_b2': True,
    'delete_local_after_upload': True
})
```

---

## 📊 Comparison

### Lines of Code Comparison

**Before:**
```python
# 10 lines
response = requests.post('/generate_manifest', json={
    'actor_name': 'Tom Hanks'
})
data = response.json()
manifest = data['manifest']

response = requests.post('/create_tiktok_video', json={
    'manifest': manifest,
    'upload_to_b2': True,
    'delete_local_after_upload': True,
    'output_filename': 'tom_hanks_video.mp4'
})
result = response.json()
```

**After:**
```python
# 5 lines
response = requests.post('/generate_manifest', json={'actor_name': 'Tom Hanks'})
data = response.json()

result = requests.post('/create_tiktok_video',
    json=data['video_creation_payload']
).json()
```

**50% less code!** 🎉

---

## 🧪 Testing

### Test the New Payload

```bash
# Start server
python launcher.py

# In another terminal, test the simplified workflow
python simple_actor_to_cloud_workflow.py "Emma Watson"
```

### Manual Test with cURL

```bash
# Step 1: Generate manifest
curl -X POST http://localhost:8080/generate_manifest \
  -H "Content-Type: application/json" \
  -d '{"actor_name": "Tom Hanks"}' \
  | jq '.video_creation_payload' > payload.json

# Step 2: Create video using payload
curl -X POST http://localhost:8080/create_tiktok_video \
  -H "Content-Type: application/json" \
  -d @payload.json
```

---

## 📚 Updated Documentation

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Updated with new response structure and examples
- **[simple_actor_to_cloud_workflow.py](simple_actor_to_cloud_workflow.py)** - New simplified example script

---

## 💡 Benefits

1. **Less Code**: 50% reduction in code required
2. **Fewer Mistakes**: No need to remember to add `upload_to_b2` and `delete_local_after_upload`
3. **Consistent Naming**: Automatic filename generation from actor name
4. **Ready for Production**: Payload includes everything needed
5. **Still Flexible**: Can modify or ignore the payload if you need custom settings

---

## 🎉 Summary

The `/generate_manifest` endpoint now returns a **complete, ready-to-use payload** that includes:

- ✅ Manifest
- ✅ `upload_to_b2: true`
- ✅ `delete_local_after_upload: true`
- ✅ Auto-generated output filename
- ✅ B2 credentials (if provided)

**Usage:**
```python
# Generate manifest
data = requests.post('/generate_manifest', json={'actor_name': 'Actor'}).json()

# Create video (one line!)
result = requests.post('/create_tiktok_video', json=data['video_creation_payload']).json()
```

**Result:** Video in cloud with shareable URL - automatically! 🚀
