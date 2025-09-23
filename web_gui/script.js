// Store movie data for each button
const movieData = {};
let currentEditingButton = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeFileInputs();
});

function initializeEventListeners() {
    // Movie button click handlers
    const movieButtons = document.querySelectorAll('.movie-btn');
    movieButtons.forEach(button => {
        button.addEventListener('click', function() {
            openMovieModal(this);
        });
    });

    // Modal event listeners
    const modal = document.getElementById('movieModal');
    const closeBtn = document.querySelector('.close');
    const saveBtn = document.getElementById('saveMovieBtn');
    const cancelBtn = document.getElementById('cancelMovieBtn');

    closeBtn.addEventListener('click', closeMovieModal);
    cancelBtn.addEventListener('click', closeMovieModal);
    saveBtn.addEventListener('click', saveMovie);

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeMovieModal();
        }
    });

    // Generate manifest button
    document.getElementById('generateBtn').addEventListener('click', createTikTokVideo);

    // Exit button
    document.getElementById('exitBtn').addEventListener('click', exitApplication);

    // Browse output directory button
    document.getElementById('browseOutputBtn').addEventListener('click', function() {
        // Note: Web browsers don't allow direct directory selection for security reasons
        // This is a placeholder - in a real implementation, you might use a file API or server-side directory picker
        alert('Directory selection is limited in web browsers. Please type the full path to your desired output directory.');
    });

    // API key visibility toggles
    document.getElementById('toggleOmdbKey').addEventListener('click', function() {
        togglePasswordVisibility('omdbApiKey', 'toggleOmdbKey');
    });

    document.getElementById('toggleTmdbKey').addEventListener('click', function() {
        togglePasswordVisibility('tmdbApiKey', 'toggleTmdbKey');
    });
}

function initializeFileInputs() {
    // Actor headshot file input
    const headshotInput = document.getElementById('actorHeadshot');
    const headshotFileName = document.getElementById('headshotFileName');

    headshotInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            headshotFileName.textContent = this.files[0].name;
        } else {
            headshotFileName.textContent = 'No file selected';
        }
    });

    // Background audio file input
    const audioInput = document.getElementById('backgroundAudio');
    const audioFileName = document.getElementById('audioFileName');

    audioInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            audioFileName.textContent = this.files[0].name;
        } else {
            audioFileName.textContent = 'assets/background_audio.mp3';
        }
    });

    // Background video file input
    const videoInput = document.getElementById('backgroundVideo');
    const videoFileName = document.getElementById('videoFileName');

    videoInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            videoFileName.textContent = this.files[0].name;
        } else {
            videoFileName.textContent = 'assets/background_video.mp4';
        }
    });

    // Movie poster file input in modal
    const posterInput = document.getElementById('moviePoster');
    const posterFileName = document.getElementById('posterFileName');

    posterInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            posterFileName.textContent = this.files[0].name;
        } else {
            posterFileName.textContent = 'No file selected';
        }
    });
}

function togglePasswordVisibility(inputId, buttonId) {
    const input = document.getElementById(inputId);
    const button = document.getElementById(buttonId);

    if (input.type === 'password') {
        input.type = 'text';
        button.textContent = '🙈';
    } else {
        input.type = 'password';
        button.textContent = '👁️';
    }
}

function openMovieModal(button) {
    currentEditingButton = button;
    const modal = document.getElementById('movieModal');
    const buttonId = `${button.dataset.row}_${button.dataset.col}`;

    // Clear previous data
    document.getElementById('movieTitle').value = '';
    document.getElementById('movieYear').value = '';
    document.getElementById('moviePoster').value = '';
    document.getElementById('posterFileName').textContent = 'No file selected';

    // If editing existing movie, populate fields
    if (movieData[buttonId]) {
        const movie = movieData[buttonId];
        document.getElementById('movieTitle').value = movie.title || '';
        document.getElementById('movieYear').value = movie.release_year || '';
        if (movie.poster_path) {
            document.getElementById('posterFileName').textContent = movie.poster_path.split('/').pop();
        }
    }

    modal.style.display = 'block';
    document.getElementById('movieTitle').focus();
}

function closeMovieModal() {
    const modal = document.getElementById('movieModal');
    modal.style.display = 'none';
    currentEditingButton = null;
}

function saveMovie() {
    const title = document.getElementById('movieTitle').value.trim();

    if (!title) {
        alert('Movie title is required!');
        return;
    }

    const year = document.getElementById('movieYear').value.trim();
    const posterFile = document.getElementById('moviePoster').files[0];

    const movieInfo = {
        title: title
    };

    if (year) {
        movieInfo.release_year = year;
    }

    if (posterFile) {
        // In a real application, you'd upload the file to a server
        // For now, we'll just store the file name
        movieInfo.poster_path = posterFile.name;
    }

    // Store movie data
    const buttonId = `${currentEditingButton.dataset.row}_${currentEditingButton.dataset.col}`;
    movieData[buttonId] = movieInfo;

    // Update button text and appearance
    const displayTitle = title.length > 15 ? title.substring(0, 15) + '...' : title;
    currentEditingButton.textContent = displayTitle;
    currentEditingButton.classList.add('filled');
    currentEditingButton.title = title; // Show full title on hover

    closeMovieModal();
}

function validateForm() {
    // Check actor name
    const actorName = document.getElementById('actorName').value.trim();
    if (!actorName) {
        alert('Actor/Actress name is required!');
        return false;
    }

    // Check if all movie slots are filled
    for (let row = 0; row < 3; row++) {
        for (let col = 0; col < 3; col++) {
            const buttonId = `${row}_${col}`;
            if (!movieData[buttonId]) {
                alert(`Please add a movie for Row ${row + 1}, Button ${col + 1}`);
                return false;
            }
        }
    }

    return true;
}

function createTikTokVideo() {
    if (!validateForm()) {
        return;
    }

    const outputFileName = document.getElementById('outputFileName').value.trim();
    const outputDirectory = document.getElementById('outputDirectory').value.trim();

    if (!outputFileName) {
        alert('Please specify an output file name!');
        return;
    }

    const manifest = buildManifest();

    // Show progress section
    const progressSection = document.getElementById('progressSection');
    const generateBtn = document.getElementById('generateBtn');

    progressSection.style.display = 'block';
    generateBtn.disabled = true;
    generateBtn.textContent = 'Creating Video...';

    updateProgress(10, 'Building manifest...');

    // Send request to create video
    fetch('/create_tiktok_video', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            manifest: manifest,
            output_path: outputDirectory,
            output_filename: outputFileName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateProgress(100, 'Video created successfully!');
            showSuccessMessage(`Video saved to: ${data.output_path}`);

            if (data.output) {
                document.getElementById('outputLog').textContent = data.output;
            }
        } else {
            updateProgress(0, 'Error creating video');
            showErrorMessage(data.message);

            if (data.errors) {
                document.getElementById('outputLog').textContent = data.errors;
            }
        }
    })
    .catch(error => {
        updateProgress(0, 'Network error');
        showErrorMessage('Failed to communicate with server: ' + error.message);
    })
    .finally(() => {
        generateBtn.disabled = false;
        generateBtn.textContent = 'Create TikTok Video';
    });
}

function buildManifest() {
    const manifest = {};
    const hintNames = ['first_hint', 'second_hint', 'third_hint'];

    // Add hints
    for (let i = 0; i < 3; i++) {
        const caption = document.getElementById(`caption${i + 1}`).value.trim();
        const movies = [];

        for (let j = 0; j < 3; j++) {
            const buttonId = `${i}_${j}`;
            movies.push(movieData[buttonId]);
        }

        manifest[hintNames[i]] = {
            caption: caption,
            movies: movies
        };
    }

    // Add answer
    const actorName = document.getElementById('actorName').value.trim();
    const answer = {
        caption: actorName
    };

    const headshotFile = document.getElementById('actorHeadshot').files[0];
    if (headshotFile) {
        answer.image_path = headshotFile.name;
    }

    manifest.answer = answer;

    // Add background files
    const audioFile = document.getElementById('backgroundAudio').files[0];
    const videoFile = document.getElementById('backgroundVideo').files[0];

    manifest.background_audio = audioFile ? audioFile.name : 'assets/background_audio.mp3';
    manifest.background_video = videoFile ? videoFile.name : 'assets/background_video.mp4';

    // Add API keys if provided
    const omdbApiKey = document.getElementById('omdbApiKey').value.trim();
    const tmdbApiKey = document.getElementById('tmdbApiKey').value.trim();

    if (omdbApiKey) {
        manifest.omdb_api_key = omdbApiKey;
    }

    if (tmdbApiKey) {
        manifest.tmdb_api_key = tmdbApiKey;
    }

    return manifest;
}

function updateProgress(percentage, message) {
    document.getElementById('progressFill').style.width = percentage + '%';
    document.getElementById('progressText').textContent = message;
}

function showSuccessMessage(message) {
    const progressSection = document.getElementById('progressSection');
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    progressSection.appendChild(successDiv);
}

function showErrorMessage(message) {
    const progressSection = document.getElementById('progressSection');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    progressSection.appendChild(errorDiv);
}

function exitApplication() {
    // Show confirmation dialog
    const confirmed = confirm('Are you sure you want to exit the TikTok Creator application?');

    if (confirmed) {
        // Disable the exit button to prevent multiple clicks
        const exitBtn = document.getElementById('exitBtn');
        exitBtn.disabled = true;
        exitBtn.textContent = 'Shutting down...';

        // Send shutdown request to server
        fetch('/shutdown', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        })
        .then(response => {
            // Show farewell message
            document.body.innerHTML = `
                <div style="
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background-color: #000;
                    color: #fff;
                    font-family: Arial, sans-serif;
                    text-align: center;
                ">
                    <h1 style="font-size: 3rem; margin-bottom: 20px;">👋</h1>
                    <h2 style="font-size: 2rem; margin-bottom: 10px;">Thanks for using TikTok Creator!</h2>
                    <p style="font-size: 1.2rem; color: #ccc;">The application is shutting down...</p>
                    <p style="font-size: 1rem; color: #888; margin-top: 20px;">You can safely close this tab now.</p>
                </div>
            `;

            // Try to close the tab/window after a short delay
            setTimeout(() => {
                // Modern browsers restrict window.close() for security reasons
                // It only works if the window was opened by a script
                if (window.opener || window.history.length === 1) {
                    window.close();
                } else {
                    // If we can't close the tab, just show a message
                    document.body.innerHTML += `
                        <div style="
                            position: fixed;
                            bottom: 20px;
                            left: 50%;
                            transform: translateX(-50%);
                            background-color: #333;
                            color: #fff;
                            padding: 10px 20px;
                            border-radius: 5px;
                            font-size: 14px;
                        ">
                            Please close this tab manually (browser security limitation)
                        </div>
                    `;
                }
            }, 2000);
        })
        .catch(error => {
            console.error('Error during shutdown:', error);
            // Even if the request fails, show the farewell message
            // The server is probably already shutting down
            document.body.innerHTML = `
                <div style="
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background-color: #000;
                    color: #fff;
                    font-family: Arial, sans-serif;
                    text-align: center;
                ">
                    <h1 style="font-size: 3rem; margin-bottom: 20px;">👋</h1>
                    <h2 style="font-size: 2rem; margin-bottom: 10px;">Thanks for using TikTok Creator!</h2>
                    <p style="font-size: 1.2rem; color: #ccc;">Application has been shut down.</p>
                    <p style="font-size: 1rem; color: #888; margin-top: 20px;">You can safely close this tab now.</p>
                </div>
            `;
        });
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // ESC to close modal
    if (event.key === 'Escape') {
        const modal = document.getElementById('movieModal');
        if (modal.style.display === 'block') {
            closeMovieModal();
        }
    }

    // Enter to save movie when in modal
    if (event.key === 'Enter') {
        const modal = document.getElementById('movieModal');
        if (modal.style.display === 'block') {
            event.preventDefault();
            saveMovie();
        }
    }
});