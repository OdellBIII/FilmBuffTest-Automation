import sys
import json
from moviepy import ImageClip, CompositeVideoClip, TextClip, ColorClip, concatenate_videoclips, AudioFileClip
import numpy as np

black = (0, 0, 0)

class ThreeColumnClip:
    def __init__(self, caption, image_paths, size):
        self.caption = caption
        self.image_paths = image_paths
        self.size = size
    
def create_title_card(text, video_size, duration=3, fontsize=70, color='white', bg_color=black):
    """
    Creates a title card clip with specified text.
    
    Args:
        text (str): Text to display on the title card
        video_size (tuple): Size of the video (width, height)
        duration (int): Duration of the title card in seconds
        fontsize (int): Font size of the text
        color (str): Text color
        bg_color (str): Background color
    
    Returns:
        ImageClip: A MoviePy ImageClip representing the title card
    """
    
    # Create a background color clip
    bg_clip = ColorClip(size=video_size, color=bg_color).with_duration(duration)
    
    # Create a text clip
    txt_clip = (TextClip(text=text, font_size=fontsize,
                         color=color, size=video_size,
                         method='label', text_align='center',
                         margin=(100, 0, 100, 0))
                .with_duration(duration)
                .with_position('center'))
    
    # Composite the text over the background
    title_card = CompositeVideoClip([bg_clip, txt_clip], size=video_size)
    
    return title_card

def create_answer_clip(answer_text, actor_headshot_path, video_size, duration=3, fontsize=70, color='white', bg_color=black):
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
    bg_clip = ColorClip(size=video_size, color=bg_color).with_duration(duration)

    # Create a text clip
    txt_clip = (TextClip(text=answer_text, font_size=fontsize,
                         color=color, size=video_size,
                         method='label', text_align='center',
                         margin=(100, 0, 100, 0))
                .with_duration(duration)
                .with_position(('center', -500)))

    # Load actor headshot image
    headshot_clip = ImageClip(actor_headshot_path).with_duration(duration).with_position(('center', 'center'))

    # Composite the text and headshot over the background
    answer_clip = CompositeVideoClip([bg_clip, txt_clip, headshot_clip], size=video_size)

    return answer_clip

def create_column_animation_clip(three_column_clip : ThreeColumnClip, current_time=0, 
                            video_size=(1920, 1080), fps=30):
    """
    Creates a video where 3 images appear fullscreen then shrink to form a 1 x 3 grid.
    Compatible with MoviePy v2.0+
    
    Args:
        json_file_path (str): Path to JSON file containing array of 9 image paths
        output_video_path (str): Output video file path
        video_size (tuple): Video dimensions (width, height)
        fps (int): Frames per second
    """

    if not isinstance(three_column_clip.image_paths, list) or len(three_column_clip.image_paths) != 3:
        raise ValueError("Three column clip must contain an array of exactly 3 image paths")

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
    
    clips = []
    current_time = 0

    # Append a title card
    title_clip = create_title_card(
        three_column_clip.caption,
        video_size=video_size,
        duration=5, fontsize=140,
        color='white', bg_color=black
    ) 
    clips.insert(0, title_clip)
    current_time += 5  # Add title duration to current time
    
    for i, image_path in enumerate(three_column_clip.image_paths):
        # Load image
        img_clip = ImageClip(image_path)
        
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
    final_video = CompositeVideoClip(clips, size=video_size)
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
    
    clips = []
    current_time = 0
    title_clip = create_title_card(
        "Can you\n guess this\n actor from\n only their\n films?",
        video_size=video_size,
        duration=5, fontsize=140,
        color='white', bg_color=black
    )
    clips.append(title_clip)
    current_time += title_clip.duration  # Add title duration to current time
    for (key, hint) in data.items():
        if "hint" not in key.lower():
            continue

        print(hint)
        if not isinstance(hint, dict) or "caption" not in hint or "image_paths" not in hint:
            raise ValueError("Each hint must be a dictionary with 'caption' and 'image_paths' keys")

        caption = hint["caption"]
        image_paths = hint["image_paths"]
        if not isinstance(image_paths, list) or len(image_paths) != 3:
            raise ValueError("Each caption must have exactly 3 image paths")

        three_column_clip = ThreeColumnClip(caption, image_paths, video_size)
        hint_clip = create_column_animation_clip(three_column_clip, current_time, video_size, fps)
        clips.append(hint_clip)
        current_time += hint_clip.duration

    the_answer_is_clip = create_title_card(
        "The answer is ...",
        video_size=video_size,
        duration=3, fontsize=140,
        color='white', bg_color=black
    )
    clips.append(the_answer_is_clip)
    current_time += the_answer_is_clip.duration

    # Append answer clip
    answer = data["answer"]
    answer_clip = create_answer_clip(answer["caption"], answer["image_path"], video_size, duration=5, fontsize=70, color='white', bg_color=black)
    clips.append(answer_clip)
    current_time += answer_clip.duration

    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.with_duration(current_time)
    # Add background audio
    background_audio_path = data["background_audio"]
    background_audio_clip = AudioFileClip(background_audio_path).with_volume_scaled(0.1).with_duration(final_video.duration)
    final_video = final_video.with_audio(background_audio_clip)

    # Write video file
    final_video.write_videofile(output_video_path, fps=fps, codec='libx264', threads=4)
    
    print(f"Video created successfully: {output_video_path}")
    print(f"Total duration: {current_time} seconds")

def create_sample_json(json_path="images.json"):
    """
    Creates a sample JSON file with placeholder image paths.
    Replace these paths with your actual image file paths.
    """
    sample_images = [
        "image1.jpg",
        "image2.jpg", 
        "image3.jpg",
        "image4.jpg",
        "image5.jpg",
        "image6.jpg",
        "image7.jpg",
        "image8.jpg",
        "image9.jpg"
    ]
    
    with open(json_path, 'w') as f:
        json.dump(sample_images, f, indent=2)
    
    print(f"Sample JSON file created: {json_path}")
    print("Please update the image paths in the JSON file with your actual image file paths.")


if __name__ == "__main__":
    # Example usage
    if sys.argv and len(sys.argv) > 1:
        manifest_file = sys.argv[1]
    else:
        manifest_file = "input/manifest.json"
    
    try:

        create_tiktok_from_json(
            json_file_path=manifest_file,
            output_video_path="output/output_video.mp4",
            video_size=(1080, 1920),
            fps=30
        )

    except FileNotFoundError:
        print("JSON file not found. Creating sample JSON file...")
        create_sample_json("images.json")
        print("Please update the image paths in 'images.json' and run the script again.")
    except Exception as e:
        print(f"Error: {e}")