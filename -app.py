#!/home/jack/Desktop/content/env/bin/python
import sys
from search import search
#import clean_images
import subprocess
import logging
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from flask import jsonify, send_file , Response
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import datetime
import glob
import json
#import ffmpeg
from werkzeug.utils import secure_filename
import time
#import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import pygame
import random
from gtts import gTTS

from io import BytesIO
import base64
import imageio
import shutil
from pydub import AudioSegment
import logging
# Define the Flask application
app = Flask(__name__)  

app.secret_key = os.urandom(24)
# Create a formatter for the log messages
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
# Create a logger object
logger = logging.getLogger(__name__)
# Set the logging level (e.g., DEBUG, INFO, ERROR)
logger.setLevel(logging.DEBUG)
# Create a file handler to write log messages to a file
file_handler = logging.FileHandler('Logs/app.log')
# Set the logging level for the file handler
file_handler.setLevel(logging.DEBUG)
# Create a formatter for the log messages
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
# Set the formatter for the file handler
file_handler.setFormatter(formatter)
# Add the file handler to the logger
logger.addHandler(file_handler)
# Now you can use the logger to log messages
#logger.debug('This is a debug message')
#logger.info('This is an info message')
#logger.warning('This is a warning message')
#logger.error('This is an error message')

# Create a file handler to write log messages to a file
handler = RotatingFileHandler('Logs/app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

# Add the file handler to the Flask app logger
app.logger.addHandler(handler)
# Set up logging
logging.basicConfig(level=logging.DEBUG)
# use the search function as a route

app.add_url_rule('/search', 'search', search)
def zip_lists(list1, list2):
    return zip(list1, list2)

app.jinja_env.filters['zip'] = zip_lists

def get_all_mp4_videos():
    mp4_videos = []
    for root, dirs, files in os.walk('static'):
        for file in files:
            if file.endswith('.mp4'):
                mp4_videos.append(os.path.join(root, file))
    return mp4_videos

def generate_thumbnails(mp4_videos, thumbnail_size=120):
    for video in mp4_videos:
        thumbnail_path = os.path.splitext(video)[0] + '.jpg'
        print(f'Generating thumbnail for video: {video} at path: {thumbnail_path}')
        os.system(f'ffmpeg -hide_banner -i "{video}" -ss 00:00:01 -vf scale={thumbnail_size}:-1 -vframes 1 -y "{thumbnail_path}"')
        print(f'Thumbnail generated at path: {thumbnail_path}')

@app.route('/thumbnails')
def thumbnails():
    mp4_videos = get_all_mp4_videos()
    generate_thumbnails(mp4_videos)
    thumbnail_paths = [os.path.splitext(video)[0] + '.jpg' for video in mp4_videos]
    video_paths = [os.path.splitext(video)[0] + '.mp4' for video in mp4_videos]
    return render_template('thumbnails.html', thumbnail_paths=thumbnail_paths, video_paths=video_paths)

@app.route('/')
def index():
    image_dir = 'static/images'
    image_files = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]
    random_image_file = random.choice(image_files)
    return render_template('index.html', random_image_file=random_image_file)

@app.route('/add_text', methods=['GET', 'POST'])
def add_text():
    if request.method == 'POST':
        text = request.form['text']
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        text = f'Text Entry: {timestamp} {text}'
        with open('chat.txt', 'a') as file:
            file.write(f'\n{text}')
        return render_template('add_text.html', message='Text added successfully')
    else:
        return render_template('add_text.html')
# Mp3 page with file upload and textarea to enter text
# Route for the text to speech page
@app.route('/text_mp3', methods=['GET', 'POST'])
def text_mp3():
    if request.method == 'POST':
        # Get the text from the textarea
        text = request.form['text']
        # Remove whitespace from the text
        text = text.replace(" ", "")
        # Create a filename based on the first 20 characters of the text
        filename = "static/audio_mp3/" + text[:20] + ".mp3"
        filename = filename.strip()  # remove the newline character
        # Create a gTTS object and save the audio file
        tts = gTTS(text)
        filename = filename.strip() 
        tts.save(filename)
        # Play the mp3 file
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        # Stop pygame and exit the program
        pygame.mixer.quit()
        pygame.quit()
        # Return the text and filename to the template
        return render_template('text_mp3.html', text=text, filename=filename)
    else:
        # Render the home page template
        return render_template('text_mp3.html')

@app.route('/select_playmp3', methods=['GET', 'POST'])
def select_playmp3():
    # Get the list of mp3 files in the static/audio_mp3/ directory
    mp3_files = [f for f in os.listdir('static/audio_mp3/') if f.endswith('.mp3')]
    if request.method == 'POST':
        # Get the selected MP3 file from the dropdown list
        mp3_file = request.form['mp3_file']
        # Play the selected mp3 file
        pygame.mixer.init()
        pygame.mixer.music.load('static/audio_mp3/' + mp3_file)
        pygame.mixer.music.play()
        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        # Stop pygame and exit the program
        pygame.mixer.quit()
        pygame.quit()
    # Render the template with the list of mp3 files
    return render_template('select_playmp3.html', mp3_files=mp3_files)
@app.route('/select_mp3', methods=['GET', 'POST'])
def select_mp3():
    mp3_dir = os.path.join(app.static_folder, 'audio_mp3')
    mp3_filename = os.path.join(mp3_dir, request.form['mp3_filename'])  # Define mp3_filename here

    if request.method == 'POST':
        selected_mp3 = mp3_filename
        # Process the selected MP3 file here
        return 'Selected MP3: {}'.format(selected_mp3)
    else:
        mp3_files = [f for f in os.listdir(mp3_dir) if f.endswith('.mp3')]
        return render_template('select_mp3.html', mp3_files=mp3_files)

@app.route('/convert_mp3_to_wav', methods=['GET', 'POST'])
def convert_mp3_to_wav():
    if request.method == 'POST':
        if 'mp3_file' not in request.files:
            return 'No MP3 file provided'

        mp3_file = request.files['mp3_file']
        if mp3_file.filename == '':
            return 'No selected file'

        mp3_filename = mp3_file.filename
        mp3_path = os.path.join(app.static_folder, 'audio_mp3', mp3_filename)
        mp3_file.save(mp3_path)

        wav_filename = 'input_audio.wav'
        wav_path = os.path.join('content/sample_data', wav_filename)

        try:
            sound = AudioSegment.from_mp3(mp3_path)
            sound.export(wav_path, format='wav')
            return 'MP3 file converted to WAV successfully'
        except Exception as e:
            return f'Error converting MP3 to WAV: {str(e)}'
    else:
        return render_template('convert_mp3_to_wav.html')
  
@app.route('/convert_image_to_video', methods=['GET', 'POST'])
def convert_image_to_video():
    if request.method == 'POST':
        # Load the image from the upload form
        image_file = request.files['image']
        image_path = os.path.join(app.static_folder, 'images', 'uploads', image_file.filename)
        image_file.save(image_path)

        # Load the audio file
        audio_path = 'content/sample_data/input_audio.wav'

        # Create an output video file name
        video_path = 'content/sample_data/input_video.mp4'

        # Set up the video and audio clips
        image_clip = ImageClip(image_path).set_duration(get_audio_duration(audio_path))
        audio_clip = AudioSegment.from_wav(audio_path)

        # Combine the image and audio clips into a video
        video_clip = image_clip.set_audio(audio_clip)

        # Write the video clip to the output file
        video_clip.write_videofile(video_path, codec='libx264', fps=30)

        return f'Video created: {video_path}'

    # If method is GET, show the upload form
    return render_template('convert_image_to_video.html')

def get_audio_duration(audio_file):
    audio = AudioSegment.from_file(audio_file)
    duration = audio.duration_seconds
    return duration




     
if __name__ == '__main__':
    app.run(debug=True)
