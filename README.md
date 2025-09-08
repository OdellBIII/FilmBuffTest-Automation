# Cinephile Tiktok Automation
This tool automates the process of creating cinephile quiz tiktok videos
## Installation
- Install docker
### Build the image
Build from main
`docker build -t cinephile-automator-image .`
Modify the manifest
Modify the manifest to include the images and audios you want. Put all files in the audio or img directories
Run the container
`docker run --rm -v ./input:/app/input -v ./output:/app/output --name cinephile-automator cinephile-automator-image`
The resulting video will be found in output
## Ideas?
- Modify the json file format to include subtitles and only list movies on screen from those sections
- Add voice clips for the text
- Add background music files