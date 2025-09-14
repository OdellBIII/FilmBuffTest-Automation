# Cinephile Tiktok Automation
This tool automates the process of creating FilmBuffTest tiktok videos
## Installation
1. Install [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation) for your OS
2. Install python 3.9 with pyenv and set it as local default
`pyenv install 3.9 && pyenv local 3.9`
3. Install virtualenv
`pip install --user virtualenv`
4. Create virtualenv
`virtualenv venv`
5. Activate the virtual environment
`source venv/bin/activate`
6. Install dependencies
`pip install -r requirements.txt`
7. Export OMDB API key
`export OMDB_API_KEY=<OMDB_API_KEY>`
## Usage
1. Move all images to `input/img` directory
2. Move all audio files to `input/audio` directory
3. Edit manifest to have the correct file path and names. The order in which the images
are listed in the file will be the order they appear in the video.
4. Activate the virtual environment if not activated already
`source venv/bin/activate`
5. Run the script `python main.py`
6. Wait for the video to complete (should take ~10 minutes depending on hardware) and the file should be in `output/output_video.mp4`

## Config file 
```
{
    "first_hint": {
        "caption": "Cinephile\nLevel\nHints",
        "movies": [
            {
                "title": "The Phoenician Scheme",
                "poster_path": "input/img/the_phoenician_scheme.jpg", // Optional field. Poster can be automatically downloaded
                "release_year": "2023" // Optional field, but it is required if you need a particular movie from a specific year (think remakes)
            },
            {
                "title": "Asteroid City"
            },
            {
                "title": "Saving Private Ryan"
            }
        ]
    },
    "second_hint": {
        "caption": "Average Movie\nEnjoyer Level\nHints",
        "movies": [
            {
                "title": "The Phoenician Scheme",
                "poster_path": "input/img/the_phoenician_scheme.jpg",
                "release_year": "2023"
            },
            {
                "title": "Asteroid City"
            },
            {
                "title": "Saving Private Ryan"
            }
        ]
    },
    "answer": {
        "caption": "Christian Bale",
        "image_path": "input/img/christian_bale.jpeg"
    },
    "background_audio": "input/audio/background_audio.mp3",
    "background_video": "input/video/background.mp4"
}
```
## Ideas?
- Add voice clips for the text