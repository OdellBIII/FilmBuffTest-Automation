from flask import Flask, send_from_directory, request, jsonify
import os
import json

app = Flask(__name__)

# Set the web_gui directory as the template and static folder
web_gui_dir = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    """Serve the main HTML page"""
    with open(os.path.join(web_gui_dir, 'index.html'), 'r') as file:
        return file.read()

@app.route('/style.css')
def styles():
    """Serve the CSS file"""
    return send_from_directory(web_gui_dir, 'style.css', mimetype='text/css')

@app.route('/script.js')
def scripts():
    """Serve the JavaScript file"""
    return send_from_directory(web_gui_dir, 'script.js', mimetype='application/javascript')

@app.route('/save_manifest', methods=['POST'])
def save_manifest():
    """Save the manifest file to the server"""
    try:
        manifest_data = request.json

        # Save to the input directory (one level up from web_gui)
        input_dir = os.path.join(os.path.dirname(web_gui_dir), 'input')
        os.makedirs(input_dir, exist_ok=True)

        manifest_path = os.path.join(input_dir, 'manifest.json')

        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=4)

        return jsonify({
            'success': True,
            'message': f'Manifest saved to {manifest_path}',
            'path': manifest_path
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving manifest: {str(e)}'
        }), 500

@app.route('/create_tiktok_video', methods=['POST'])
def create_tiktok_video():
    """Create TikTok video using the provided manifest and output settings"""
    try:
        data = request.json
        manifest = data.get('manifest')
        output_path = data.get('output_path', '.')
        output_filename = data.get('output_filename', 'output_video.mp4')

        if not manifest:
            return jsonify({
                'success': False,
                'message': 'No manifest data provided'
            }), 400

        # Save manifest to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_manifest:
            json.dump(manifest, temp_manifest, indent=4)
            temp_manifest_path = temp_manifest.name

        try:
            # Set API keys from manifest if provided
            if 'omdb_api_key' in manifest:
                os.environ['GTA_OMDB_API_KEY'] = manifest['omdb_api_key']
            if 'tmdb_api_key' in manifest:
                os.environ['GTA_TMDB_API_KEY'] = manifest['tmdb_api_key']

            # Import and run the create_tiktok_from_json function directly
            import sys
            main_dir = os.path.dirname(web_gui_dir)
            sys.path.insert(0, main_dir)

            from main import create_tiktok_from_json

            # Construct full output path
            if output_path == '.' or output_path == '':
                full_output_path = os.path.join(main_dir, output_filename)
            else:
                full_output_path = os.path.join(output_path, output_filename)

            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(full_output_path)
            os.makedirs(output_dir, exist_ok=True)

            # Call the function directly
            create_tiktok_from_json(
                json_file_path=temp_manifest_path,
                output_video_path=full_output_path,
                video_size=(1080, 1920),
                fps=30
            )

            return jsonify({
                'success': True,
                'message': 'TikTok video created successfully!',
                'output_path': full_output_path,
                'output': f'Video saved to: {full_output_path}'
            })

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
            os.kill(os.getpid(), signal.SIGINT)
            return jsonify({'success': True, 'message': 'Server shutting down...'})

        shutdown_func()
        return jsonify({'success': True, 'message': 'Server shutting down...'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error during shutdown: {str(e)}'})

if __name__ == '__main__':
    print(f"Starting TikTok Creator Web Interface...")
    print(f"Open your browser and go to: http://localhost:8080")
    print(f"Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=8080)