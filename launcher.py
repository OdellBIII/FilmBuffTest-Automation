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