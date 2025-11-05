# Backblaze B2 Setup Guide

This guide will help you set up Backblaze B2 cloud storage for automatic video uploads.

## Why Backblaze B2?

- **Super cheap**: $0.005/GB/month (5x cheaper than AWS S3)
- **Free tier**: First 10GB of storage is FREE
- **Free egress**: 1GB/day of downloads for free
- **Easy to use**: S3-compatible API
- **Perfect for your use case**: Automatic upload after video creation, local file cleanup

---

## Step 1: Create a Backblaze B2 Account

1. Go to [backblaze.com/b2](https://www.backblaze.com/b2)
2. Sign up for a free account
3. Verify your email address
4. You'll get:
   - 10GB of free storage
   - 1GB/day of free downloads
   - No credit card required for the free tier

---

## Step 2: Create a Bucket

1. Log in to your Backblaze B2 account
2. Click **"Buckets"** in the left sidebar
3. Click **"Create a Bucket"**
4. Configure your bucket:
   - **Bucket Name**: Choose a unique name (e.g., `my-tiktok-videos`)
   - **Files in Bucket**: Choose **"Private"** (recommended) or **"Public"** if you want direct sharing
   - **Default Encryption**: Choose as preferred (optional)
   - **Object Lock**: Leave disabled (not needed)
5. Click **"Create a Bucket"**

---

## Step 3: Generate Application Keys

1. In the B2 web console, click **"App Keys"** in the left sidebar
2. Scroll down to **"Add a New Application Key"**
3. Configure the key:
   - **Name of Key**: Give it a descriptive name (e.g., `tiktok-creator-key`)
   - **Allow access to Bucket(s)**: Select the bucket you created
   - **Type of Access**: Choose **"Read and Write"**
   - **Allow List All Bucket Names**: Check this box (optional but recommended)
   - **File name prefix**: Leave blank
   - **Duration**: Leave blank (no expiration)
4. Click **"Create New Key"**

5. **IMPORTANT**: You'll see two values:
   ```
   keyID: 005a1b2c3d4e5f6g7h8i9j0k
   applicationKey: K005aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890
   ```

   **⚠️  COPY THESE NOW!** The `applicationKey` will only be shown once and cannot be retrieved later.

---

## Step 4: Configure Environment Variables

You have two options for providing B2 credentials:

### Option A: Environment Variables (Recommended)

Create or edit your `.env` file in the project root:

```bash
# Backblaze B2 Configuration
B2_APPLICATION_KEY_ID=005a1b2c3d4e5f6g7h8i9j0k
B2_APPLICATION_KEY=K005aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890
B2_BUCKET_NAME=my-tiktok-videos
```

**On macOS/Linux:**
```bash
export B2_APPLICATION_KEY_ID="005a1b2c3d4e5f6g7h8i9j0k"
export B2_APPLICATION_KEY="K005aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890"
export B2_BUCKET_NAME="my-tiktok-videos"
```

**On Windows:**
```cmd
set B2_APPLICATION_KEY_ID=005a1b2c3d4e5f6g7h8i9j0k
set B2_APPLICATION_KEY=K005aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890
set B2_BUCKET_NAME=my-tiktok-videos
```

### Option B: Pass via API Request

You can also pass credentials in the API request (see API documentation).

---

## Step 5: Install Dependencies

Make sure you have the B2 SDK installed:

```bash
pip install -r requirements.txt
```

Or install it directly:

```bash
pip install b2sdk==2.6.0
```

---

## Step 6: Test the Integration

### Test 1: Upload a Video Using the Client Directly

```bash
python clients/B2StorageClient.py path/to/video.mp4
```

Expected output:
```
🔐 Authenticating with Backblaze B2...
✅ Connected to bucket: my-tiktok-videos
📤 Uploading path/to/video.mp4 (14.50 MB) to B2...
   Remote name: video.mp4
✅ Upload successful!
   File ID: 4_z123456789abcdef_f987654321fedcba_d20231104_m123456_c005_v0001234_t0012
   File Name: video.mp4
```

### Test 2: Create a Video with Automatic B2 Upload

Create a test script:

```python
from main import create_tiktok_from_json

result = create_tiktok_from_json(
    json_file_path="example/manifest.json",
    output_video_path="test_video.mp4",
    upload_to_b2=True,
    delete_local_after_upload=True
)

print(f"B2 URL: {result['b2_url']}")
print(f"Local deleted: {result['local_deleted']}")
```

---

## Step 7: Using B2 Upload via Web UI

The web interface doesn't currently have B2 upload controls built in, but you can enable it via API:

```javascript
fetch('/create_tiktok_video', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    manifest: { /* your manifest */ },
    output_filename: "my_video.mp4",
    upload_to_b2: true,  // Enable B2 upload
    delete_local_after_upload: true,  // Delete local file after upload
    // Optional: Override env vars
    b2_application_key_id: "your_key_id",
    b2_application_key: "your_key",
    b2_bucket_name: "your_bucket"
  })
})
```

---

## Accessing Your Uploaded Videos

### For Private Buckets:

Download URLs are provided in the response, but they require authentication. You can:

1. Use the Backblaze B2 web console to browse and download files
2. Generate time-limited download URLs (feature coming soon)
3. Make the bucket public if you want direct sharing

### For Public Buckets:

The download URL in the response will work directly:
```
https://f005.backblazeb2.com/file/my-tiktok-videos/my_video.mp4
```

---

## Cost Estimate

**Example: 100 TikTok videos (15MB each = 1.5GB total)**

- **Storage**: FREE (under 10GB free tier)
- **Uploads**: FREE (always free)
- **Downloads**: ~$0.01 if you exceed 1GB/day free tier

**Total monthly cost**: $0.00 - $0.01 🎉

---

## Troubleshooting

### Error: "B2 credentials must be provided"

- Make sure environment variables are set
- Check that variable names are exactly: `B2_APPLICATION_KEY_ID`, `B2_APPLICATION_KEY`, `B2_BUCKET_NAME`
- On macOS/Linux, variables must be exported: `export B2_APPLICATION_KEY_ID="..."`

### Error: "Bucket does not exist"

- Check the bucket name spelling
- The client will automatically create the bucket if it doesn't exist (if you have permission)

### Error: "Unauthorized"

- Double-check your Application Key ID and Application Key
- Make sure the key has access to the bucket
- Regenerate the key if needed (in B2 console)

### Upload is slow

- B2 upload speeds depend on your internet connection
- For a 15MB video, typical upload time is 10-30 seconds on a good connection

---

## Security Best Practices

1. **Never commit credentials to git**
   - Add `.env` to `.gitignore`
   - Use environment variables or secret management

2. **Use application keys with limited scope**
   - Create keys with access to only the specific bucket needed
   - Use "Read and Write" not "All Buckets"

3. **Rotate keys periodically**
   - Delete old keys after creating new ones
   - Update environment variables with new keys

4. **Keep buckets private by default**
   - Only make public if you need direct URL sharing
   - Use signed URLs for temporary access (advanced)

---

## Next Steps

- ✅ Set up environment variables
- ✅ Create your first bucket
- ✅ Test upload with a sample video
- 🔄 Integrate into your workflow
- 📊 Monitor storage usage in B2 console

---

## Support

- **Backblaze B2 Documentation**: [backblaze.com/b2/docs](https://www.backblaze.com/b2/docs/)
- **B2 API Reference**: [backblaze.com/b2/docs/b2_list_buckets.html](https://www.backblaze.com/b2/docs/b2_list_buckets.html)
- **Pricing Calculator**: [backblaze.com/b2/cloud-storage-pricing.html](https://www.backblaze.com/b2/cloud-storage-pricing.html)
