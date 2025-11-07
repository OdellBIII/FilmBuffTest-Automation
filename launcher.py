#!/usr/bin/env python3
"""
Launcher script for the TikTok Creator application.
This script starts the Flask web server and optionally opens the browser.
"""

import os
import sys
import webbrowser
import threading
import time
from flask import Flask, send_from_directory, request, jsonify
import json
import tempfile

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Create Flask app
app = Flask(__name__)

# Get the web GUI directory path
web_gui_dir = resource_path('web_gui')

@app.route('/')
def index():
    """Serve the main HTML page"""
    html_path = os.path.join(web_gui_dir, 'index.html')
    with open(html_path, 'r', encoding='utf-8') as file:
        return file.read()

@app.route('/style.css')
def styles():
    """Serve the CSS file"""
    return send_from_directory(web_gui_dir, 'style.css', mimetype='text/css')

@app.route('/script.js')
def scripts():
    """Serve the JavaScript file"""
    return send_from_directory(web_gui_dir, 'script.js', mimetype='application/javascript')

@app.route('/create_tiktok_video', methods=['POST'])
def create_tiktok_video():
    """Create TikTok video using the provided manifest and output settings"""
    try:
        data = request.json
        manifest = data.get('manifest')
        output_path = data.get('output_path', '.')
        output_filename = data.get('output_filename', 'output_video.mp4')
        upload_to_b2 = data.get('upload_to_b2', False)
        delete_local_after_upload = data.get('delete_local_after_upload', True)

        if not manifest:
            return jsonify({
                'success': False,
                'message': 'No manifest data provided'
            }), 400

        # Save manifest to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_manifest:
            json.dump(manifest, temp_manifest, indent=4)
            temp_manifest_path = temp_manifest.name

        try:
            # Set API keys from manifest if provided
            if 'omdb_api_key' in manifest:
                os.environ['GTA_OMDB_API_KEY'] = manifest['omdb_api_key']
            if 'tmdb_api_key' in manifest:
                os.environ['GTA_TMDB_API_KEY'] = manifest['tmdb_api_key']

            # Set B2 credentials from data if provided
            if 'b2_application_key_id' in data:
                os.environ['B2_APPLICATION_KEY_ID'] = data['b2_application_key_id']
            if 'b2_application_key' in data:
                os.environ['B2_APPLICATION_KEY'] = data['b2_application_key']
            if 'b2_bucket_name' in data:
                os.environ['B2_BUCKET_NAME'] = data['b2_bucket_name']

            # Import and run the create_tiktok_from_json function directly
            # Add the bundle directory to Python path
            bundle_dir = resource_path('')
            if bundle_dir not in sys.path:
                sys.path.insert(0, bundle_dir)

            from main import create_tiktok_from_json

            # Construct full output path
            if output_path == '.' or output_path == '':
                full_output_path = os.path.join(os.getcwd(), output_filename)
            else:
                full_output_path = os.path.join(output_path, output_filename)

            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(full_output_path)
            os.makedirs(output_dir, exist_ok=True)

            # Call the function directly
            result = create_tiktok_from_json(
                json_file_path=temp_manifest_path,
                output_video_path=full_output_path,
                video_size=(1080, 1920),
                fps=30,
                upload_to_b2=upload_to_b2,
                delete_local_after_upload=delete_local_after_upload
            )

            # Build response based on result
            response = {
                'success': True,
                'message': 'TikTok video created successfully!',
                'output_path': full_output_path,
                'output': f'Video saved to: {full_output_path}'
            }

            # Add B2 upload information if uploaded
            if result.get('uploaded_to_b2'):
                response['uploaded_to_b2'] = True
                response['b2_url'] = result.get('b2_url')
                response['b2_file_id'] = result.get('b2_file_id')
                response['b2_file_name'] = result.get('b2_file_name')
                response['local_deleted'] = result.get('local_deleted', False)
                if result.get('local_deleted'):
                    response['message'] = 'TikTok video created and uploaded to B2! Local file deleted.'
                else:
                    response['message'] = 'TikTok video created and uploaded to B2!'
            elif 'upload_error' in result:
                response['upload_to_b2_failed'] = True
                response['upload_error'] = result['upload_error']

            return jsonify(response)

        finally:
            # Clean up temporary file
            if os.path.exists(temp_manifest_path):
                os.unlink(temp_manifest_path)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()

        return jsonify({
            'success': False,
            'message': f'Error creating TikTok video: {str(e)}',
            'errors': error_details
        }), 500

@app.route('/generate_manifest', methods=['POST'])
def generate_manifest():
    """
    Generate a manifest from an actor's name using ActorMovieRecommender.
    Returns a manifest structure ready to be used with /create_tiktok_video endpoint.
    """
    try:
        data = request.json
        actor_name = data.get('actor_name')

        if not actor_name:
            return jsonify({
                'success': False,
                'message': 'Actor name is required'
            }), 400

        # Optional parameters
        background_audio = data.get('background_audio', 'assets/background_audio.mp3')
        background_video = data.get('background_video', 'assets/background_video.mp4')
        hint_captions = data.get('hint_captions', [
            "Hard Level\nHints",
            "Medium Level\nHints",
            "Easy Level\nHints"
        ])

        # Set TMDB API key if provided in request
        if 'tmdb_api_key' in data:
            os.environ['GTA_TMDB_API_KEY'] = data['tmdb_api_key']

        # Import ActorMovieRecommender
        bundle_dir = resource_path('')
        if bundle_dir not in sys.path:
            sys.path.insert(0, bundle_dir)

        from clients.ActorMovieRecommender import ActorMovieRecommender

        # Get top 9 movies for the actor
        print(f"🎬 Fetching top movies for: {actor_name}")
        recommender = ActorMovieRecommender()
        movies_json_str = recommender.get_actor_top_movies(actor_name, limit=9)
        movies_data = json.loads(movies_json_str)

        # Split movies into 3 groups of 3 (sorted by popularity already)
        all_movies = movies_data['movies']

        if len(all_movies) < 9:
            return jsonify({
                'success': False,
                'message': f'Not enough movies found for {actor_name}. Found {len(all_movies)}, need 9.',
                'movies_found': len(all_movies)
            }), 400

        # Create manifest structure
        # Most popular movies (hardest hint) go first
        manifest = {
            'first_hint': {
                'caption': hint_captions[0],
                'movies': [
                    {
                        'title': all_movies[0]['title'],
                        'release_year': all_movies[0]['release_year']
                    },
                    {
                        'title': all_movies[1]['title'],
                        'release_year': all_movies[1]['release_year']
                    },
                    {
                        'title': all_movies[2]['title'],
                        'release_year': all_movies[2]['release_year']
                    }
                ]
            },
            'second_hint': {
                'caption': hint_captions[1],
                'movies': [
                    {
                        'title': all_movies[3]['title'],
                        'release_year': all_movies[3]['release_year']
                    },
                    {
                        'title': all_movies[4]['title'],
                        'release_year': all_movies[4]['release_year']
                    },
                    {
                        'title': all_movies[5]['title'],
                        'release_year': all_movies[5]['release_year']
                    }
                ]
            },
            'third_hint': {
                'caption': hint_captions[2],
                'movies': [
                    {
                        'title': all_movies[6]['title'],
                        'release_year': all_movies[6]['release_year']
                    },
                    {
                        'title': all_movies[7]['title'],
                        'release_year': all_movies[7]['release_year']
                    },
                    {
                        'title': all_movies[8]['title'],
                        'release_year': all_movies[8]['release_year']
                    }
                ]
            },
            'answer': {
                'caption': actor_name
            },
            'background_audio': background_audio,
            'background_video': background_video
        }

        # Add API keys to manifest if provided
        if 'omdb_api_key' in data:
            manifest['omdb_api_key'] = data['omdb_api_key']
        if 'tmdb_api_key' in data:
            manifest['tmdb_api_key'] = data['tmdb_api_key']

        print(f"✅ Generated manifest with {len(all_movies)} movies")

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

        # Return the video creation payload directly - ready to send to /create_tiktok_video
        return jsonify(video_creation_payload)

    except ValueError as ve:
        return jsonify({
            'success': False,
            'message': str(ve)
        }), 404

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()

        return jsonify({
            'success': False,
            'message': f'Error generating manifest: {str(e)}',
            'errors': error_details
        }), 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Gracefully shutdown the Flask server"""
    try:
        # Get the Werkzeug shutdown function
        shutdown_func = request.environ.get('werkzeug.server.shutdown')
        if shutdown_func is None:
            # Alternative method for newer Flask versions
            import os
            import signal
            print("\n🛑 Shutdown requested - stopping server...")
            os.kill(os.getpid(), signal.SIGINT)
            return jsonify({'success': True, 'message': 'Server shutting down...'})

        print("\n🛑 Shutdown requested - stopping server...")
        shutdown_func()
        return jsonify({'success': True, 'message': 'Server shutting down...'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error during shutdown: {str(e)}'})

def open_browser():
    """Open the default web browser to the application URL"""
    time.sleep(1.5)  # Wait for Flask to start
    webbrowser.open('http://localhost:8080')

def main():
    """Main entry point for the application"""
    print("=" * 60)
    print("🎬 TikTok Creator - Web Interface")
    print("=" * 60)
    print()
    print("Starting web server...")
    print("🌐 Application will be available at: http://localhost:8080")
    print()
    print("📋 Instructions:")
    print("  1. Fill out movie hints for each row")
    print("  2. Enter actor/actress name")
    print("  3. Specify output file name and location")
    print("  4. Click 'Create TikTok Video'")
    print()
    print("Press Ctrl+C to stop the application")
    print("=" * 60)

    # Start browser in a separate thread
    if '--no-browser' not in sys.argv:
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()

    # Start Flask app
    try:
        app.run(debug=False, host='0.0.0.0', port=8080, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for using TikTok Creator!")
        sys.exit(0)

if __name__ == '__main__':
    main()