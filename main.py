import sys
import os
import json
from moviepy import ImageClip, CompositeVideoClip, TextClip, ColorClip, concatenate_videoclips, AudioFileClip, VideoFileClip 
from moviepy.video.fx import Loop
from MoviePosterFinder.OMDBClient import OMDBClient
from clients.TMDBClient import TMDBClient
from clients.ElevenLabsClient import ElevenLabsClient

black = (0, 0, 0)
OMDB_API_KEY = os.getenv("GTA_OMDB_API_KEY")
TMDB_API_KEY = os.getenv("GTA_TMDB_API_KEY")
ELEVEN_LABS_API_KEY = os.getenv("GTA_ELEVEN_LABS_API_KEY")

class Movie:
    def __init__(self, title, poster_path=None, release_year=None):
        self.title = title
        self.poster_path = poster_path
        self.release_year = release_year

class ThreeColumnClip:
    def __init__(self, caption, movies, size):
        self.caption = caption
        self.movies = movies
        self.size = size

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if relative_path == None:
        return None
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def generate_voice_over(text: str, eleven_labs_client: ElevenLabsClient = None) -> str:
    """
    Generate voice-over audio for given text using Eleven Labs

    Args:
        text (str): Text to convert to speech
        eleven_labs_client (ElevenLabsClient): Eleven Labs client instance

    Returns:
        str: Path to generated audio file, or None if voice-over is disabled/failed
    """
    print(f"🎤 Debug: generate_voice_over called with text: '{text[:50]}...'")
    print(f"🎤 Debug: eleven_labs_client exists: {eleven_labs_client is not None}")

    if not eleven_labs_client or not text.strip():
        print(f"🎤 Debug: Skipping voice-over - client: {eleven_labs_client is not None}, text: '{text.strip()}'")
        return None

    try:
        # Clean text for speech (remove special characters that might cause issues)
        clean_text = text.replace('\n', ' ').replace('\r', ' ').strip()
        if not clean_text:
            print("🎤 Debug: No clean text after processing")
            return None

        print(f"🎤 Debug: Generating voice-over for: '{clean_text}'")

        # Create a unique filename based on the text content
        import hashlib
        text_hash = hashlib.md5(clean_text.encode()).hexdigest()[:8]
        filename = f"voice_{text_hash}.mp3"
        save_path = resource_path(f"assets/{filename}")

        # Generate voice-over
        audio_path = eleven_labs_client.text_to_speech(clean_text, save_path=save_path)
        print(f"🎤 Debug: Voice-over generated successfully: {audio_path}")
        return audio_path

    except Exception as e:
        print(f"❌ Warning: Failed to generate voice-over for text '{text[:50]}...': {e}")
        return None

def create_title_card(text, video_size, duration=3, fontsize=70, color='white', bg_color=black, bg_video_path=None, voice_over_path=None):
    """
    Creates a title card clip with specified text.

    Args:
        text (str): Text to display on the title card
        video_size (tuple): Size of the video (width, height)
        duration (int): Duration of the title card in seconds
        fontsize (int): Font size of the text
        color (str): Text color
        bg_color (str): Background color
        bg_video_path (str): Path to background video
        voice_over_path (str): Path to voice-over audio file

    Returns:
        CompositeVideoClip: A MoviePy CompositeVideoClip representing the title card
    """
    
    # Create a background color clip
    bg_clip = None
    if bg_video_path:
        bg_clip = VideoFileClip(bg_video_path, target_resolution=video_size)
        bg_clip = Loop(duration=duration).apply(bg_clip)
    else:
        bg_clip = ColorClip(size=video_size, color=bg_color).with_duration(duration)

    # Create a text clip
    txt_clip = (TextClip(text=text, font_size=fontsize,
                         color=color, size=video_size,
                         method='label', text_align='center',
                         margin=(100, 0, 100, 0))
                .with_duration(duration)
                .with_position('center'))
    
    # Composite the text over the background
    title_card = CompositeVideoClip([bg_clip, txt_clip], size=video_size, use_bgclip=True)

    # Add voice-over audio if provided
    print(f"🔊 Debug: voice_over_path = {voice_over_path}")
    print(f"🔊 Debug: voice_over_path exists = {voice_over_path and os.path.exists(voice_over_path) if voice_over_path else False}")

    if voice_over_path and os.path.exists(voice_over_path):
        try:
            print(f"🔊 Debug: Loading audio from {voice_over_path}")
            voice_audio = AudioFileClip(voice_over_path)
            print(f"🔊 Debug: Audio duration: {voice_audio.duration}, Video duration: {duration}")

            # Adjust duration to match video or vice versa
            if voice_audio.duration > duration:
                # If voice-over is longer, extend video duration
                title_card = title_card.with_duration(voice_audio.duration)
                print(f"🔊 Debug: Extended video duration to {voice_audio.duration}")
            else:
                # If voice-over is shorter, trim it to video duration
                voice_audio = voice_audio.with_duration(duration)
                print(f"🔊 Debug: Trimmed audio duration to {duration}")

            title_card = title_card.with_audio(voice_audio)
            print("🔊 Debug: Audio successfully added to title card")
        except Exception as e:
            print(f"❌ Warning: Could not add voice-over audio: {e}")
    else:
        print("🔊 Debug: No voice-over audio to add")

    return title_card

def create_answer_clip(answer_text, actor_headshot_path, video_size, duration=3, fontsize=70, color='white', bg_color=black, bg_video_path=None, voice_over_path=None):
    """
    Creates an answer clip with specified text and actor headshot.
    
    Args:
        answer_text (str): Text to display as the answer
        actor_headshot_path (str): Path to the actor's headshot image
        video_size (tuple): Size of the video (width, height)
        duration (int): Duration of the answer clip in seconds
        fontsize (int): Font size of the text
        color (str): Text color
        bg_color (str): Background color
    
    Returns:
        CompositeVideoClip: A MoviePy CompositeVideoClip representing the answer clip
    """
    # Create a background color clip
    bg_clip = None
    if bg_video_path:
        bg_clip = VideoFileClip(bg_video_path, target_resolution=video_size)
        bg_clip = Loop(duration=duration).apply(bg_clip)
    else:
        bg_clip = ColorClip(size=video_size, color=bg_color).with_duration(duration)

    # Create a text clip
    txt_clip = (TextClip(text=answer_text, font_size=fontsize,
                         color=color, size=video_size,
                         method='label', text_align='center',
                         margin=(100, 0, 100, 0))
                .with_duration(duration)
                .with_position(('center', -500)))

    # Load actor headshot image
    headshot_clip = ImageClip(actor_headshot_path).with_duration(duration).with_position(('center', 'center')).resized(height=600)

    # Composite the text and headshot over the background
    answer_clip = CompositeVideoClip([bg_clip, txt_clip, headshot_clip], size=video_size, use_bgclip=True)

    # Add voice-over audio if provided
    if voice_over_path and os.path.exists(voice_over_path):
        try:
            voice_audio = AudioFileClip(voice_over_path)
            # Adjust duration to match video or vice versa
            if voice_audio.duration > duration:
                # If voice-over is longer, extend video duration
                answer_clip = answer_clip.with_duration(voice_audio.duration)
            else:
                # If voice-over is shorter, trim it to video duration
                voice_audio = voice_audio.with_duration(duration)

            answer_clip = answer_clip.with_audio(voice_audio)
        except Exception as e:
            print(f"Warning: Could not add voice-over audio: {e}")

    return answer_clip

def create_column_animation_clip(three_column_clip : ThreeColumnClip, current_time=0,
                            video_size=(1920, 1080), fps=30, bg_video_path=None, eleven_labs_client=None):
    """
    Creates a video where 3 images appear fullscreen then shrink to form a 1 x 3 grid.
    Compatible with MoviePy v2.0+
    
    Args:
        json_file_path (str): Path to JSON file containing array of 9 image paths
        output_video_path (str): Output video file path
        video_size (tuple): Video dimensions (width, height)
        fps (int): Frames per second
    """

    if not isinstance(three_column_clip.movies, list) or len(three_column_clip.movies) != 3:
        raise ValueError("Three column clip must contain an array of exactly 3 movie objects")

    video_width, video_height = video_size
    
    # Calculate grid cell dimensions
    cell_width = video_width // 3
    cell_height = video_height // 3
    
    # Define grid positions (top-left corner of each cell)
    grid_positions = []
    for row in range(3):
        x = 1 * cell_width
        y = row * cell_height
        grid_positions.append((x, y))

    bg_clip = None
    target_duration = 5 + len(three_column_clip.movies) * 4.0  # 5 seconds for title + 4 seconds per movie
    #target_duration = 60
    if bg_video_path:
        bg_clip = VideoFileClip(bg_video_path, target_resolution=video_size)
        bg_clip = Loop(duration=target_duration).apply(bg_clip)
    else:
        bg_clip = ColorClip(size=video_size, color=black).with_duration(target_duration)

    clips = []
    current_time = 0
    clips.append(bg_clip)

    # Generate voice-over for caption
    caption_voice_path = generate_voice_over(three_column_clip.caption, eleven_labs_client) if eleven_labs_client else None

    # Append a title card
    title_clip = create_title_card(
        three_column_clip.caption,
        video_size=video_size,
        duration=5, fontsize=140,
        color='white', bg_video_path=bg_video_path,
        voice_over_path=caption_voice_path
    )
    clips.append(title_clip)
    current_time += title_clip.duration  # Use actual clip duration

    for i, movie in enumerate(three_column_clip.movies):
        # Load image
        img_clip = ImageClip(movie.poster_path)
        # Phase 1: Fullscreen display (1.5 seconds)
        # Resize to cover full screen while maintaining aspect ratio
        fullscreen_clip = img_clip.resized(height=video_height).with_position('center')
        
        # If image is narrower than screen after height resize, resize by width instead
        if fullscreen_clip.w < video_width:
            fullscreen_clip = img_clip.resized(width=video_width).with_position('center')
        
        fullscreen_clip = fullscreen_clip.with_start(current_time).with_duration(1.5)
        clips.append(fullscreen_clip)
        
        # Phase 2: Shrink and move to grid position (1.5 seconds)
        grid_x, grid_y = grid_positions[i]
        
        # Create the shrinking/moving clip using lambda functions for smooth animation
        def make_transition_clip(img, start_time, start_w, start_h, start_x, start_y, 
                               end_w, end_h, end_x, end_y):
            
            def resize_func(t):
                progress = min(t / 1.5, 1.0)
                # Smooth easing function (ease-in-out)
                progress = 3 * progress**2 - 2 * progress**3
                
                w = start_w + (end_w - start_w) * progress
                h = start_h + (end_h - start_h) * progress
                
                # Calculate scale factor based on original image dimensions
                original_w = img.w
                original_h = img.h
                
                # Maintain aspect ratio by scaling uniformly
                scale_w = w / original_w
                scale_h = h / original_h
                scale = min(scale_w, scale_h)  # Use minimum to maintain aspect ratio
                
                return scale
            
            def position_func(t):
                progress = min(t / 1.5, 1.0)
                # Smooth easing function (ease-in-out)
                progress = 3 * progress**2 - 2 * progress**3
                
                x = start_x + (end_x - start_x) * progress
                y = start_y + (end_y - start_y) * progress
                return (x, y)
            
            # Create the animated clip
            clip = img.resized(resize_func).with_position(position_func)
            clip = clip.with_start(start_time).with_duration(1.5)
            
            return clip
        
        # Calculate start and end parameters for the transition
        start_size = (fullscreen_clip.w, fullscreen_clip.h)
        end_size = (cell_width, cell_height)
        
        # Start position (center of screen)
        start_pos = ((video_width - start_size[0]) // 2, 
                    (video_height - start_size[1]) // 2)
        end_pos = (grid_x, grid_y)
        
        # Create base clip for transition
        transition_base = img_clip.resized(height=video_height)
        if transition_base.w < video_width:
            transition_base = img_clip.resized(width=video_width)
            
        transition_clip = make_transition_clip(
            img_clip, current_time + 1.5,
            start_size[0], start_size[1], start_pos[0], start_pos[1],
            end_size[0], end_size[1], end_pos[0], end_pos[1]
        )
        
        clips.append(transition_clip)
        
        # Keep the image in its final grid position for remaining duration
        if i < 3:  # Don't add static clip for the last image
            final_clip = img_clip.resized((cell_width, cell_height))
            final_clip = final_clip.with_position((grid_x, grid_y))
            final_clip = final_clip.with_start(current_time + 3.0)
            final_clip = final_clip.with_duration((3 - i) * 3.0 + 3.0)  # Duration until video ends
            clips.append(final_clip)
        
        current_time += 4.0  # Each image takes 3 seconds total (1.5 + 1.5)

    # Create final composite video
    final_video = CompositeVideoClip(clips, size=video_size, use_bgclip=True)
    final_video = final_video.with_duration(current_time)

    return final_video

def create_tiktok_from_json(json_file_path, output_video_path="output_column_animation.mp4", 
                         video_size=(1080, 1920), fps=30):
    """
    Creates a TikTok-style vertical video that combines multiple ThreeColumnClip instances.
    """

    # Load data from JSON
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("JSON file must contain a dictionary with captions as keys and lists of image paths as values")

    # Create OMDB client for retrieving movie posters
    omdb_client = OMDBClient(api_key=OMDB_API_KEY)
    # Create TMDB client for retrieving actor headshots
    tmdb_client = TMDBClient(api_key=TMDB_API_KEY)
    # Create Eleven Labs client for voice-overs if enabled
    eleven_labs_client = None
    enable_voice_overs = data.get("enable_voice_overs", False)

    print(f"🔍 Debug: enable_voice_overs = {enable_voice_overs}")
    print(f"🔍 Debug: ELEVEN_LABS_API_KEY exists = {bool(ELEVEN_LABS_API_KEY)}")
    print(f"🔍 Debug: Full manifest data keys: {list(data.keys())}")

    if enable_voice_overs and ELEVEN_LABS_API_KEY:
        try:
            eleven_labs_client = ElevenLabsClient(api_key=ELEVEN_LABS_API_KEY)
            print("✅ Eleven Labs voice-overs enabled")

            # Test the client with a simple phrase
            test_save_path = resource_path("assets/test_voice.mp3")
            test_audio_path = eleven_labs_client.text_to_speech("Test voice over", save_path=test_save_path)
            print(f"✅ Test voice-over generated: {test_audio_path}")

        except Exception as e:
            print(f"⚠️ Warning: Could not initialize Eleven Labs client: {e}")
            print("Continuing without voice-overs...")
    elif enable_voice_overs:
        print("⚠️ Warning: Voice-overs enabled but no Eleven Labs API key found")
        print("Continuing without voice-overs...")
    else:
        print("ℹ️ Voice-overs disabled in settings")

    # Get background video path if provided
    background_video_path = data["background_video"]
    if background_video_path == None or not os.path.exists(background_video_path):
        background_video_path = resource_path("assets/background.mp4")

    clips = []
    current_time = 0

    # Generate voice-over for intro title
    intro_text = "Can you guess this actor from only their films?"
    intro_voice_path = generate_voice_over(intro_text, eleven_labs_client) if eleven_labs_client else None

    title_clip = create_title_card(
        "Can you\n guess this\n actor from\n only their\n films?",
        video_size=video_size,
        duration=5, fontsize=140,
        color='white', bg_color=black, bg_video_path=background_video_path,
        voice_over_path=intro_voice_path
    )
    clips.append(title_clip)
    current_time += title_clip.duration  # Add title duration to current time
    for (key, hint) in data.items():
        if "hint" not in key.lower():
            continue

        print(hint)
        if not isinstance(hint, dict) or "caption" not in hint or "movies" not in hint:
            raise ValueError("Each hint must be a dictionary with 'caption' and 'movies' keys")

        caption = hint["caption"]
        movie_data = hint["movies"]
        if not isinstance(movie_data, list) or len(movie_data) != 3:
            raise ValueError("Each caption must have exactly 3 movie data entries")

        movies = []
        # Check that each movie datum is a dict with 'title' and optional 'poster_path'
        # If 'poster_path' is missing, use OMDBClient to download the poster
        for movie_datum in movie_data:
            if not isinstance(movie_datum, dict) or "title" not in movie_datum:
                raise ValueError("Each movie data entry must be a dictionary with at least a 'title' key")
            title = movie_datum["title"]
            poster_path = movie_datum.get("poster_path")
            release_year = movie_datum.get("release_year")
            if not poster_path:
                try:
                    normalized_title = title.lower().replace(" ", "_").replace(":", "").replace("-", "_")
                    poster_path = resource_path(f"assets/{normalized_title}.jpg")
                    poster_path = omdb_client.download_movie_poster(title, save_path=poster_path, release_year=release_year)
                except Exception as e:
                    print(f"Error downloading poster for '{title}': {e}")
                    poster_path = resource_path("input/img/placeholder.jpg")

            movies.append(Movie(title=title, poster_path=poster_path, release_year=release_year))

        three_column_clip = ThreeColumnClip(caption, movies, video_size)
        hint_clip = create_column_animation_clip(three_column_clip, current_time, video_size, fps, bg_video_path=background_video_path, eleven_labs_client=eleven_labs_client)
        clips.append(hint_clip)
        current_time += hint_clip.duration

    # Generate voice-over for "The answer is" text
    answer_intro_text = "The answer is"
    answer_intro_voice_path = generate_voice_over(answer_intro_text, eleven_labs_client) if eleven_labs_client else None

    the_answer_is_clip = create_title_card(
        "The answer is ...",
        video_size=video_size,
        duration=3, fontsize=140,
        color='white', bg_color=black, bg_video_path=background_video_path,
        voice_over_path=answer_intro_voice_path
    )
    clips.append(the_answer_is_clip)
    current_time += the_answer_is_clip.duration

    # Append answer clip
    answer = data["answer"]
    print("Checking if answer has an image path field")
    actor_headshot_path = ""
    print("Image path is not there")
    actor_name = answer["caption"]
    if "image_path" not in answer:
        actor_headshot_path = resource_path(f"assets/{actor_name.lower().replace(' ', '_')}.jpg")
        tmdb_client.download_actor_headshot(actor_name, save_path=actor_headshot_path)
    else:
        actor_headshot_path = answer["image_path"]

    # Generate voice-over for actor name
    actor_voice_path = generate_voice_over(actor_name, eleven_labs_client) if eleven_labs_client else None

    answer_clip = create_answer_clip(answer["caption"], actor_headshot_path, video_size, duration=5, fontsize=70, color='white', bg_color=black, bg_video_path=background_video_path, voice_over_path=actor_voice_path)
    clips.append(answer_clip)
    current_time += answer_clip.duration

    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.with_duration(current_time)
    # Add background audio
    background_audio_path = data["background_audio"]
    if background_audio_path and os.path.exists(background_audio_path):
        background_audio_clip = AudioFileClip(background_audio_path).with_volume_scaled(0.1).with_duration(final_video.duration)
        final_video = final_video.with_audio(background_audio_clip)

    # Write video file
    final_video.write_videofile(output_video_path, fps=fps, codec='libx264', threads=4)
    
    print(f"Video created successfully: {output_video_path}")
    print(f"Total duration: {current_time} seconds")

if __name__ == "__main__":
    # Example usage
    if sys.argv and len(sys.argv) > 1:
        manifest_file = sys.argv[1]
    else:
        print("Usage: python main.py <path_to_manifest.json>")
        sys.exit(1)

    # Check for required environment variables
    required_env_vars = ["GTA_OMDB_API_KEY", "GTA_TMDB_API_KEY"]
    for var in required_env_vars:
        if var not in os.environ:
            raise ValueError(f"Missing required environment variable: {var}")

    try:
        create_tiktok_from_json(
            json_file_path=manifest_file,
            output_video_path="output_video.mp4",
            video_size=(1080, 1920),
            fps=30
        )
    except FileNotFoundError as fnfe:
        print(f"File not found: {fnfe}")
    except Exception as e:
        print(f"Error: {e}")