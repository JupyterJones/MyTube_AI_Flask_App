#!/mnt/HDD500/flask/FLASK/flask_venv/bin/python
import sys
sys.path.append('/mnt/HDD500/flask/FLASK')
from search import search
import clean_images
import subprocess
import logging
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from flask import jsonify, send_file , Response
import os
from logging.handlers import RotatingFileHandler
import datetime
import glob
import json
import ffmpeg
from werkzeug.utils import secure_filename
import time
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import pygame
import random
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
from io import BytesIO
import base64
import imageio
import shutil
import logging
from pydub import AudioSegment
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
logger.debug('This is a debug message')
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
# use the search function as a routeapp.secret_key = os.urandom(24)

app.config['UPLOAD_FOLDER'] = 'static/images/uploads'
app.config['RESULTS_FOLDER'] = 'static/videos/results'
app.config['THUMBNAILS_FOLDER'] = 'static/images/thumbnails'
app.config['CHECKPOINT_PATH'] = 'checkpoints/wav2lip_gan.pth'
app.config['AUDIO_PATH'] = 'content/sample_data/input_audio.wav'


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



directories = ['static/images','static/images/squares', 'static/final_videos', 'static/Dreamlike_art', 'static/squares', 'static/images/uploads', 'static/BrightColors', 'static/final_images', 'static/thumbnails']

@app.route('/')
def home():
    return render_template('choose_dir.html', directories=directories)

@app.route('/choose_dir', methods=['GET', 'POST'])
def choose_dir():
    if request.method == 'POST':
        selected_directory = request.form.get('directory', directories)
        app.logger.error('No file was selected')
        if selected_directory is None:
            # Handle the case where no directory is selected
            return 'No directory selected!'

        # Rest of the code...
        # Use the selected_directory variable in your logic to generate the video
        # Make sure to update the paths according to the selected directory

        # Get the list of image files in the selected directory
        logger.debug('SELECTED', selected_directory)
        image_filenames = random.sample(glob.glob(selected_directory + '/*.jpg'), 10)
        image_clips = []
        for filename in image_filenames:
            # Open the image file and resize it to 512x768
            image = Image.open(filename)
            #image = image.resize((512, 768), Image.ANTIALIAS)
            # Convert the PIL Image object to a NumPy array
            image_array = np.array(image)
            # Create an ImageClip object from the resized image and set its duration to 1 second
            image_clip = ImageClip(image_array).set_duration(1)
            # Append the image clip to the list
            image_clips.append(image_clip)

        # Concatenate all the image clips into a single video clip
        video_clip = concatenate_videoclips(image_clips, method='compose')
        timestr = time.strftime("%Y%m%d-%H%M%S")
        # Set the fps value for the video clip
        video_clip.fps = 24
        # Write the video clip to a file
        video_file = f'static/videos/random_images_{timestr}_video.mp4'
        output_p = 'static/videos/random_images_video.mp4'
        video_clip.write_videofile(video_file, fps=24)
        try:
            shutil.copy(video_file, output_p)
        except Exception as e:
            return f"Error occurred while copying file: {str(e)}"

        # Return the rendered template with the list of directories and output path
        return render_template('choose_dir.html', directories=directories, output_path=output_p)

    # If the request method is GET, render the form template with the list of directories
    output_p = 'static/videos/random_images_video.mp4'
    return render_template('choose_dir.html', directories=directories, output_path=output_p)



# Define route to display upload form
@app.route('/upload_file', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            app.logger.error('No file was uploaded')
            flash('Error: No file was uploaded')
            return redirect(request.url)

        app.logger.error('request.files[\'file\']')
        file = request.files['file']

        # Check if file was selected
        if file.filename == '':
            app.logger.error('No file was selected')
            flash('Error: No file was selected')
            return redirect(request.url)

        # Define allowed file extensions
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

        # Define function to check file extension
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        # Check if file is allowed
        if not allowed_file(file.filename):
             #app.logger.error(f"File '{file.filename}' is not allowed")
             app.logger.error("File '" + file.filename + "' is not allowed")
             flash("Error: File '" + file.filename + "'close is not allowed")
             return redirect(request.url)

        # Save the file
        try:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            app.logger.info(f'File {filename} saved')
        except Exception as e:
            app.logger.error(f'Error saving file: {e}')
            flash('Error: Unable to save file')
            return redirect(request.url)

        # Redirect to the result page
        return redirect(url_for('result', filename=filename))

    # Return the upload form for GET requests
    return render_template('upload_file.html')


@app.route('/result/<filename>')
def result(filename):
    return render_template('result.html', filename=filename)


@app.route('/process_images', methods=['POST', 'GET'])
def process_images():
    if request.method == 'POST':
        # read the images from the request
        img1 = Image.open(request.files['image1'].stream).convert('RGB')
        img2 = Image.open(request.files['image2'].stream).convert('L')
        img3 = Image.open(request.files['image3'].stream).convert('RGB')
    
        # resize the images to have the same shape
        img1 = img1.resize((img2.width, img2.height))
        img3 = img3.resize((img2.width, img2.height))
    
        # convert the mask to binary
        threshold = 127
        mask = Image.eval(img2, lambda px: 255 if px > threshold else 0)
    
        # apply the mask
        img = Image.composite(img1, img3, mask)
    
        # save the image to a file
        output = BytesIO()
        current_datetime = datetime.now()
        str_current_datetime = str(current_datetime)
        file_name = "static/images/"+str_current_datetime+"XXXX.jpg"
        img.save(file_name, format='JPEG')
        img.save(output, format='JPEG')
        output.seek(0)
    
        # encode the image to bytes
        img_bytes = output.getvalue()
    
        # return the image as a response
        return Response(img_bytes, mimetype='image/jpeg')
    return render_template('process_images.html')


@app.route('/blend_pil', methods=['POST', 'GET'])
def blend_pil():
    if request.method == 'POST':
        # Get the uploaded images
        img1 = request.files['img1']
        img2 = request.files['img2']
        img3 = request.files['img3']

        # Open the images using PIL
        img1_pil = Image.open(img1)
        img2_pil = Image.open(img2)
        img3_pil = Image.open(img3)

        # Blend the images
        blended_pil = Image.blend(img1_pil, img2_pil, 1/3)
        blended_pil = Image.blend(blended_pil, img3_pil, 1/3)

        # Return the blended image as a response
        # Since we are not saving it to the server, we can use a BytesIO object to avoid creating a temporary file
        img_io = BytesIO()
        blended_pil.save(img_io, 'JPEG', quality=70)
        current_datetime = datetime.now()
        str_current_datetime = str(current_datetime)
        file_name = "static/images/uploads/blended_pil"+str_current_datetime+"XXXX.jpg"
        blended_pil.save(file_name, format='JPEG')
        img_io.seek(0)
        
        # Generate the HTML for displaying the blended image in the template
        blended_image_data = base64.b64encode(img_io.getvalue()).decode('utf-8')
        blended_image_url = f"data:image/jpeg;base64,{blended_image_data}"
        #blended_image_url = blended_image_url.resize(( blended_image_url.size[0]//2, blended_image_url.size[1]//2), Image.ANTIALIAS) 
        # Pass the URL of the blended image to the template
        return render_template('show_blend_pil.html', blended_image_url=blended_image_url)      
    return render_template('blend_pil.html')
@app.route('/view_thumbs')
def view_thumbs():
    # Define the directory where the images are located
    image_directory = 'static/images/uploads'
    # Get a list of all the image files in the directory
    image_files = [f for f in os.listdir(image_directory) if f.endswith('.jpg') or f.endswith('.png')]
    # Create a list of dictionaries containing the image file name and URL
    image_list = [{'name': f, 'url': f'/images/uploads/{f}'} for f in image_files]
    # Render the template with the list of images
    return render_template('view_thumbs.html', image_list=image_list)



@app.route('/images/uploads/<filename>')
def image(filename):
    # Define the directory where the images are located
    image_directory = '/mnt/HDD500/flask/FLASK/static/images/uploads'
    # Generate the full path to the requested image file
    image_path = os.path.join(image_directory, filename)
    # Determine the file type based on the file extension
    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension == '.jpg':
        content_type = 'image/jpeg'
    elif file_extension == '.png':
        content_type = 'image/png'
    else:
        # If the file type is not recognized, return a 404 error
        print("abort(404)")
    # Return the image file as a response with the appropriate content type
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return Response(image_data, content_type=content_type)

@app.route('/add_border')
def add_border():
    images = [f for f in os.listdir('static/images/uploads/') if os.path.isfile(os.path.join('static/images/uploads/', f))]
    thumbnails = []
    for image in images:
        with Image.open('static/images/uploads/'+image) as img:
            img.thumbnail((200, 200))
            thumbnail_name = 'thumbnail_'+image
            img.save('static/thumbnails/'+thumbnail_name)
            thumbnails.append(thumbnail_name)
    return render_template('add_border.html', images=images, thumbnails=thumbnails)


@app.route('/select_border')
def select_border():
    borders = os.listdir('static/transparent_borders/')
    return render_template('select_border.html', borders=borders)

@app.route('/apply_border', methods=['POST', 'GET'])
def apply_border():
    selected_image = request.form['image']
    selected_border = request.form['border']
    try:
        with Image.open('static/images/uploads/'+selected_image) as img:
            with Image.open('static/transparent_borders/'+selected_border) as border:
                img = img.resize(border.size)
                img.paste(border, (0, 0), border)
                final_image_name = 'final_'+selected_image
                img.save('static/final_images/'+final_image_name)
        return render_template('final_image.html', final_image=final_image_name, message='Border applied successfully.')
    except Exception as e:
        error_message = f'An error occurred: {str(e)}. Please try again.'
        return render_template('apply_border.html', image=selected_image, border=selected_border, error_message=error_message)

@app.route('/select_border_image', methods=['GET'])
def select_border_image():
    try:
        image = request.args.get('image')
        if not image:
            raise ValueError('No image selected.')
        return render_template('select_border.html', image=image, borders=os.listdir('static/transparent_borders/'))
    except Exception as e:
        error_message = f'An error occurred: {str(e)}. Please try again.'
        return render_template('add_border.html', error_message=error_message)

@app.route("/make_animation")
def make_animation():
    # Get a list of all files in the final_images directory
    #image_files = os.listdir("static/final_images/")
    #DIR = "/home/jack/Desktop/HDD500/collections/gypsy_files/"
    #DIR = "/home/jack/Desktop/HDD500/collections/hippy_files/"
    DIR = "/mnt/HDD500/collections/jungle/exotic_lithograph_prints-Playground_AI_files/512x768/"
    image_files = os.listdir(DIR)
    #image_files = os.listdir("/mnt/HDD500/collections/640x640-alien/")
    # Select 20 random files from the list
    selected_files = random.sample(image_files, 30)
    
    # Load each selected file, resize it to 400x600, and save it to a temporary directory
    resized_images = []
    for filename in selected_files:
        with Image.open(DIR + filename) as img:
            img = img.resize((400, 600))
            temp_filename = "static/tmp/" + filename
            img.save(temp_filename)
            resized_images.append(temp_filename)
    
    # Create an animated GIF from the resized images
 
    gif_filename = "static/animated_gifs/animated.gif"
    with imageio.get_writer(gif_filename, mode='I', duration=1) as writer:
        for filename in resized_images:
            image = imageio.imread(filename)
            writer.append_data(image)
    import shutil

    timestr = time.strftime("%Y%m%d-%H%M%S")

  
    src = 'static/animated_gifs/animated.gif'
    dst = 'static/animated_gifs/animated' + timestr + '.gif'
    # 2nd option
    shutil.copy(src, dst) 
    # Return a template that displays the GIF
    return render_template("make_animation.html", gif_filename=gif_filename)

@app.route('/search_txt', methods=['GET', 'POST'])
def search_txt():
    if request.method == 'POST' and 'phrase' in request.form:
        phrase = request.form['phrase']
        with open('chat.txt', 'r') as file:
            lines = file.readlines()
        results = []
        for i, line in enumerate(lines):
            if phrase in line:
                start = max(0, i-5)
                end = min(len(lines), i+6)
                context = lines[start:end]
                for j, context_line in enumerate(context):
                    if phrase in context_line:
                        results.append(f'Line {start+j}: {context_line}')
                    else:
                        results.append(f'Line {start+j}: {context_line}')
        return render_template('results.html', results=results)
    return render_template('search_txt.html')

from datetime import datetime

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

@app.route('/generate_video')
def generate_video():
    # Get the pythonlist of image files in the static/final_images/ directory  
    #image_filenames = random.sample(glob.glob('static/final_images/*.jpg'),20)
    image_filenames = random.sample(glob.glob('static/video_resources/*.jpg'),30)
    print(image_filenames,end="-")
   
    image_clips = []
    for filename in image_filenames:
        # Open the image file and resize it to 512x768
        image = Image.open(filename)
        image = image.resize((512, 768), Image.ANTIALIAS)
        print(image)
        # Convert the PIL Image object to a NumPy array
        image_array = np.array(image)
        # Create an ImageClip object from the resized image and set its duration to 1 second
        image_clip = ImageClip(image_array).set_duration(1)
        
        # Append the image clip to the list
        image_clips.append(image_clip)
    
    # Concatenate all the image clips into a single video clip
    video_clip = concatenate_videoclips(image_clips, method='compose')
    timestr = time.strftime("%Y%m%d-%H%M%S")
    # Set the fps value for the video clip
    video_clip.fps = 24
    # Write the video clip to a file
    video_url = 'static/videos/random_images'+timestr+'video.mp4'
    video_clip.write_videofile(video_url, fps=24)
    
    # Return a message to the client
    return render_template('generate_video.html', video_url=video_url)
# List of directories to choose from


@app.route('/generate_video2')
def generate_video2():
    # Get the pythonlist of image files in the static/final_images/ directory  
    image_filenames = random.sample(glob.glob('static/final_images/*.jpg'),25)
    #image_filenames = random.sample(glob.glob('static/images/uploads/*.jpg'),30)
    print(image_filenames,end="-")
   
    image_clips = []
    for filename in image_filenames:
        # Open the image file and resize it to 512x768
        image = Image.open(filename)
        image = image.resize((512, 768), Image.ANTIALIAS)
        print(image)
        # Convert the PIL Image object to a NumPy array
        image_array = np.array(image)
        # Create an ImageClip object from the resized image and set its duration to 1 second
        image_clip = ImageClip(image_array).set_duration(1)
        
        # Append the image clip to the list
        image_clips.append(image_clip)
    
    # Concatenate all the image clips into a single video clip
    video_clip = concatenate_videoclips(image_clips, method='compose')
    timestr = time.strftime("%Y%m%d-%H%M%S")
    # Set the fps value for the video clip
    video_clip.fps = 24
    # Write the video clip to a file
    video_path = 'static/videos/random_images'+timestr+'video.mp4'
    video_clip.write_videofile(video_path, fps=24)
    video_clip.write_videofile('static/videos/TEMPvideo.mp4', fps=24)
    
    # Return a message to the client
    #return render_template('generate_video2.html', video_url='/static/videos/TEMPvideo.mp4')
    return render_template('generate_video2.html' ,video_url='/static/videos/TEMPvideo.mp4', video_path=video_path)


@app.route('/square_video/<path:directory>')
def square_video(directory=None):
    app.logger.info('Directory selected: %s', directory)
    if directory is None:
        app.logger.error('Error: no directory specified')
        return "Error: no directory specified"
    
    # Get the list of image files in the selected directory
    image_filenames = glob.glob(os.path.join(directory, '*.jpg'))
    if not image_filenames:
        app.logger.error('Error: no image files found in directory')
        return "Error: no image files found in directory"
    
    # Randomly select 50 image files from the list
    image_filenames = random.sample(image_filenames, 20)
    
    image_clips = []
    for filename in image_filenames:
        # Open the image file and resize it to 640x640
        image = Image.open(filename)
        image = image.resize((640, 640), Image.ANTIALIAS)
        # Convert the PIL Image object to a NumPy array
        image_array = np.array(image)
        
        # Create an ImageClip object from the resized image and set its duration to 1 second
        image_clip = ImageClip(image_array).set_duration(1)
        # Append the image clip to the list
        image_clips.append(image_clip)
    # Concatenate all the image clips into a single video clip
    video_clip = concatenate_videoclips(image_clips, method='compose')
    # Set the fps value for the video clip
    video_clip.fps = 24
    # Write the video clip to a file
    timestr = time.strftime("%Y%m%d-%H%M%S")
    video_filename = 'static/square_vids/'+timestr+'video.mp4'
    video_clip.write_videofile(video_filename, fps=24)
    video_clip.write_videofile("static/temp.mp4", fps=24)
    video_filename = "static/temp.mp4"
    return redirect(url_for('square_video', directory=directory))

@app.route('/image_directories', methods=['GET', 'POST'])
def image_directories():
    image_directories = ['static/Prodia_640x640', 'static/LineArt', 'static/Quantized', 'static/squares', 'static/BrightColors']
    if request.method == 'POST':
        # Rest of the code

        directory = request.form['directory']
        # Check that the directory parameter is not empty
        if directory:
            app.logger.info('Redirecting endpoint with directory: %s', directory)
            # Check that the directory is a valid directory path
            if os.path.isdir(directory):
                # Pass the directory value to the square_video endpoint
                app.logger.info('Redirecting to square_video endpoint with directory: %s', directory)
                return redirect(url_for('square_video', directory=directory))
            else:
                # Render an error template if the directory parameter is not a valid directory path
                app.logger.error('Invalid directory parameter: %s', directory)
                return render_template('error.html', message='Please enter a valid directory path.')
        else:
            # Render an error template if the directory parameter is empty
            app.logger.error('Directory parameter is empty')
            return render_template('error.html', message='Please enter a directory path.')
    else:
        # Pass the list of image directories to the template
        return render_template('image_directories.html', image_directories=image_directories)

@app.route('/title_page', methods=['GET', 'POST'])
def title_page():
    if request.method == 'POST':
        # Get the text input from the user
        text = request.form['text']
        app.logger.debug('XXXXXXXXXXXXX')
        app.logger.info('This is a test message')
        # Create a transparent image with size 800x600
        IMAGE = random.choice(glob.glob("static/LineArt/*.jpg"))
        image = Image.open(IMAGE)
        
        # Create a drawing context on the image
        draw = ImageDraw.Draw(image)
        
        # Define the font and font size for the text
        font = ImageFont.truetype('static/fonts/OpenSansBold.ttf', 40)
        # Split the text by newline characters
        lines = text.split("  ")


        # Calculate the size of each line and get the maximum width
        line_sizes = [draw.textsize(line, font) for line in lines]
        max_line_width = max([size[0] for size in line_sizes])

        # Calculate the total size of the text
        text_width = max_line_width
        text_height = sum([size[1] for size in line_sizes])

        # Calculate the position of the text in the center of the image
        x = (640 - text_width) / 2
        y = (640 - text_height) / 2

        # Calculate the size of the text
        text_width, text_height = draw.textsize(text, font)
        
        # Calculate the position of the text in the center of the image
        x = (640 - text_width) / 2
        y = (640 - text_height) / 2
        
        # Add the text to the image
        draw.text((x, y), text, font=font, fill=(0, 0, 0, 255))
        
        # Save the image to the static folder with a unique filename
        inc = text.replace(" ","")
        filename = os.path.join('title_pages', f'{inc}_{hash(text)}.png')
        image.save(filename)
        
        return render_template('title_page.html', filename=filename)
        
    return render_template('title_page.html')

from flask import Flask, render_template, request
import os
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, clips_array, concatenate_videoclips, TextClip

@app.route('/add_title', methods=['GET', 'POST'])
def add_title():
    # Create the final_videos directory if it does not exist
    final_videos_dir = os.path.join(app.static_folder, 'final_videos')
    if not os.path.exists(final_videos_dir):
        os.makedirs(final_videos_dir)

    if request.method == 'POST':
        app.logger.debug('Entering POST request handler for /add_title')
        # Get the paths of the selected video and title page
        video_path = os.path.join(app.static_folder, 'square_vids', request.form['video'])
        title_page_path = os.path.join(app.static_folder, 'title_pages', request.form['title_page'])
        app.logger.debug(f'video_path: {video_path}')
        app.logger.debug(f'title_page_path: {title_page_path}')

        # Load the video and title page as clips
        video_clip = VideoFileClip(video_path)
        title_page_clip = ImageClip(title_page_path).set_duration(2)

        # Add the title page to the video for the first 2 seconds
        final_clip = concatenate_videoclips([title_page_clip, video_clip.subclip(2)])

        # Save the final video to the final_videos directory
        final_filename = f"{os.path.splitext(request.form['video'])[0]}_{os.path.splitext(request.form['title_page'])[0]}.mp4"
        final_path = os.path.join(final_videos_dir, final_filename)
        app.logger.debug(f'final_path: {final_path}')
        final_clip.write_videofile(final_path)

        # Return a response to the user indicating that the video with title page was created
        message = f"The video with title page was created and saved to {final_path}"
        return render_template('add_title.html', message=message)

    # If the request method is GET, render the add_title.html template
    app.logger.debug('Entering GET request handler for /add_title')
    videos = os.listdir(os.path.join(app.static_folder, 'square_vids'))
    title_pages = os.listdir(os.path.join(app.static_folder, 'title_pages'))
    app.logger.debug(f'videos: {videos}')
    app.logger.debug(f'title_pages: {title_pages}')
    return render_template('add_title.html', videos=videos, title_pages=title_pages)

@app.route('/build_stackedvids')
def build_stackedvids():
    # Get a random video and image from the static folder
    video_filename = random.choice(glob.glob('static/square_vids/*.mp4'))
    image_filename = random.choice(glob.glob('static/squares/*.jpg'))
    
    # Load the video and image files as clips
    video_clip = VideoFileClip(video_filename)
    image_clip = ImageClip(image_filename)
    
    # Set the duration of the image clip to match the duration of the video clip
    image_clip = image_clip.set_duration(video_clip.duration)
    
    # Resize the clips to 640x640 and 640x640 respectively
    video_clip = video_clip.resize((640, 640))
    image_clip = image_clip.resize((640, 640))
    
    # Create a black clip to fill the remaining space below the image
    black_clip = ColorClip(size=(640, 640), color=(0, 0, 0)).set_duration(video_clip.duration)
    
    # Combine the clips vertically using CompositeVideoClip
    final_clip = CompositeVideoClip([
        video_clip.set_position(('center', 'top')),
        image_clip.set_position(('center', 640)),
        black_clip.set_position(('center', 640 + 640))
    ], size=(640, 1280))
    
    # Export the final clip as a video file
    timestr = time.strftime("%Y%m%d-%H%M%S")
    video_filename = 'static/stacked_vids/stacked_vids'+timestr+'video.mp4'
    final_clip_path = 'static/stacked_vids/stacked_videos.mp4'
    final_clip.write_videofile(final_clip_path)
    final_clip.write_videofile(video_filename)
    
    return render_template('/build_stackedvids.html', stackedvid_url=final_clip_path)

from moviepy.editor import *
@app.route('/build_stackedvid')
def build_stackedvid():
    # Get a random video and image from the static folder
    video_filename = random.choice(glob.glob('static/square_vids/*.mp4'))
    videofilename = random.choice(glob.glob('static/square_vids/*.mp4'))
    
    
    # Load the video and image files as clips
    video_clip = VideoFileClip(video_filename)
    videoclip = VideoFileClip(videofilename)
    
    # Set the duration of the image clip to match the duration of the video clip
    videoclip = videoclip.set_duration(video_clip.duration)
    
    # Resize the clips to 640x640 and 640x640 respectively
    video_clip = video_clip.resize((640, 640))
    videoclip = videoclip.resize((640, 640))
    
    # Create a black clip to fill the remaining space below the image
    black_clip = ColorClip(size=(640, 640), color=(0, 0, 0)).set_duration(video_clip.duration)
    
    # Combine the clips vertically using CompositeVideoClip
    final_clip = CompositeVideoClip([
        video_clip.set_position(('center', 'top')),
        videoclip.set_position(('center', 640)),
        black_clip.set_position(('center', 640 + 640))
    ], size=(640, 1280))
    
    # Export the final clip as a video file
    timestr = time.strftime("%Y%m%d-%H%M%S")
    video_filename = 'static/stacked_vids/stacked_vids'+timestr+'video.mp4'
    final_clip_path = 'static/stacked_vids/stacked_videos.mp4'
    final_clip.write_videofile(final_clip_path)
    final_clip.write_videofile(video_filename)
    
    return render_template('/build_stackedvid.html', stackedvid_url=final_clip_path)

@app.route('/clean_images', methods=['POST'])
def clean_images_route():
    clean_images()
    app.logger.error('line 210 clean_images_route')
    return redirect(url_for('index'))

@app.route('/get_gallery')
def get_gallery():
    image_dir = '/mnt/HDD500/flask/FLASK/static/images/uploads'
    image_names = os.listdir(image_dir)
    return render_template('get_gallery.html', image_names=image_names)

@app.route('/uploads/<filename>')
def send_image(filename):
    return send_from_directory('static/images/uploads', filename)

@app.route('/uploads/thumbnails/<filename>')
def send_image_thumb(filename):
    return send_from_directory('static/images/uploads/thumbnails', filename)
@app.route('/flask_info')
def flask_info():
    return render_template('flask_info.html')
@app.route('/add_effects')
def add_effects():
    return '''
        <form method="post" action="/video" enctype="multipart/form-data">
            <label for="input_video">Select input video file:</label><br>
            <input type="file" id="input_video" name="input_video"><br><br>
            <input type="submit" value="Submit">
        </form>
    '''

@app.route('/video', methods=['GET', 'POST'])
def process_video():
    DIR = "static/"
    input_video = request.files['input_video']
    
    # Save the uploaded video to a file
    input_video.save(f"{DIR}input_video.mp4")
    
    # Run FFmpeg commands
    command1 = f"ffmpeg -nostdin -i {DIR}input_video.mp4 -filter:v \"minterpolate='mi_mode=mci:mc_mode=aobmc:vsbmc=1:fps=10'\" -c:v libx264 -r 20 -pix_fmt yuv420p -c:a copy -y {DIR}output.mp4"    
    
    subprocess.run(command1, shell=True, stderr=subprocess.PIPE, universal_newlines=True)
    
    command2 = f"ffmpeg -nostdin -i {DIR}output.mp4 -vf mpdecimate,setpts=N/FRAME_RATE/TB -c:v libx264 -r 30 -pix_fmt yuv420p -c:a copy -y {DIR}mpdecimate.mp4"
    
    subprocess.run(command2, shell=True, stderr=subprocess.PIPE, universal_newlines=True)
    
    #DIR = "/home/jack/Desktop/ffmpeg_flask/"
    command3 = f"ffmpeg -i static/mpdecimate.mp4 -filter_complex \"[0:v]trim=duration=14,loop=500:1:0[v];[1:a]afade=t=in:st=0:d=1,afade=t=out:st=0.9:d=2[a1];[v][0:a][a1]concat=n=1:v=1:a=1\" -c:v libx264 -r 30 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -y static/output.mp4"
    subprocess.run(command3, shell=True, stderr=subprocess.PIPE, universal_newlines=True)
    
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    shutil.copy(f"{DIR}output.mp4", f"{DIR}{now}_output.mp4")
    logging.info(f'my_video: f"{DIR}mpdecimate.mp4"') 
    video_file="static/outputALL.mp4"     
    command4 = f'ffmpeg -i "{DIR}mpdecimate.mp4" -i "{DIR}mpdecimate.mp4" -i "{DIR}mpdecimate.mp4" -i "{DIR}mpdecimate.mp4" -i "{DIR}mpdecimate.mp4" -filter_complex "[0:v]trim=duration=15[v0];[1:v]trim=duration=15[v1];[2:v]trim=duration=15[v2];[3:v]trim=duration=15[v3];[4:v]trim=duration=15[v4];[v0][v1][v2][v3][v4]concat=n=5:v=1:a=0" -c:v libx264 -pix_fmt yuv420p -shortest -y {video_file}'
    subprocess.run(command4, shell=True, stderr=subprocess.PIPE, universal_newlines=True)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    diR = f"{DIR}/square_videos/"
    logging.info(f'diR: f"{diR}mpdecimate.mp4"')
    shutil.copy(f"{video_file}", f"{diR}{now}_outputALL.mp4")
    logging.info(f'diR: {diR}mpdecimate.mp4')
    return render_template('final.html', video_file=video_file)

def get_all_mp4_videos():
    mp4_videos = []
    for root, dirs, files in os.walk('static'):
        for file in files:
            if file.endswith('.mp4'):
                mp4_videos.append(os.path.join(root, file))
    return mp4_videos

@app.route('/play/<path:video_path>')
def play(video_path):
    return send_file(video_path)

@app.route('/select_order', methods=['GET', 'POST'])
def select_order():
    output_path = 'static/videos/concatenated_video.mp4'  # Set a default value for output_path
    if request.method == 'POST':
        # Get the order of the videos from the form data
        order = request.form.getlist('order')
        # Join the videos in the specified order
        join_videos(order, output_path)
        # Set the timestamped output path
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        new_output_path = f'static/videos/concatenated_{timestamp}XX.mp4'
        shutil.copy(output_path, new_output_path)
        # Redirect to the download page
        return redirect(url_for('download'))
    else:
        # Get the paths to the video files in the directory
        video_dir = 'static/videos'
        video_files = [os.path.join(video_dir, filename) for filename in os.listdir(video_dir) if filename.endswith('.mp4')]
        # Render the template with the list of video files and the output path
        return render_template('select_order.html', video_files=video_files, output_path=output_path)
         
def join_videos(video_paths, output_path):
    # Generate a list of input arguments for FFmpeg
    input_args = []
    for path in video_paths:
        input_args.extend(['-i', path])
    # Join the videos using FFmpeg
    subprocess.run(['ffmpeg', *input_args, '-filter_complex', 'concat=n={}:v=1:a=0'.format(len(video_paths)), '-c:v', 'libx264', '-crf', '23', '-preset', 'veryfast', '-y', output_path])
    #output_path = 'static/videos/concatenated_video.mp4'
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    new_output_path = f'static/videos/concatenated_{timestamp}XX.mp4'
    shutil.copy(output_path, new_output_path)
    
@app.route('/select_mp3', methods=['GET', 'POST'])
def select_mp3():
    mp3_dir = os.path.join(app.static_folder, 'audio_mp3')
    mp3_files = [f for f in os.listdir(mp3_dir) if f.endswith('.mp3')]

    if request.method == 'POST':
        selected_mp3 = request.form['selected_mp3']
        # Process the selected MP3 file here
        return 'Selected MP3: {}'.format(selected_mp3)
    else:
        return render_template('select_mp3.html', mp3_files=mp3_files)
@app.route('/convert_mp3_to_wav', methods=['GET', 'POST'])
def convert_mp3_to_wav():
    if request.method == 'POST':
        mp3_file = request.files['mp3_file']
        mp3_filename = mp3_file.filename
        mp3_path = os.path.join(app.static_folder, 'audio_mp3', mp3_filename)
        mp3_file.save(mp3_path)

        wav_filename = 'input_audio.wav'
        wav_path = os.path.join('sample_data', wav_filename)

        sound = AudioSegment.from_mp3(mp3_path)
        sound.export(wav_path, format='wav')

        return 'MP3 file converted to WAV successfully'
    else:
        return render_template('convert_mp3_to_wav.html')
 
from moviepy.editor import ImageClip, concatenate_videoclips
from pydub import AudioSegment

@app.route('/convert_image_to_video', methods=['GET', 'POST'])
def convert_image_to_video():
    if request.method == 'POST':
        # Load the image from the upload form
        image_file = request.files['image']
        image_path = os.path.join(app.static_folder, 'images', 'uploads', image_file.filename)
        image_file.save(image_path)

        # Load the audio file
        audio_path = 'sample_data/input_audio.wav'

        # Create an output video file name
        video_path = 'sample_data/input_video.mp4'

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

def customConvert(silf, palette, dither=False):
    ''' Convert an RGB or L mode image to use a given P image's palette.
        PIL.Image.quantize() forces dither = 1. 
        This custom quantize function will force it to 0.
        https://stackoverflow.com/questions/29433243/convert-image-to-specific-palette-using-pil-without-dithering
    '''

    silf.load()

    # use palette from reference image made below
    palette.load()
    im = silf.im.convert("P", 0, palette.im)
    # the 0 above means turn OFF dithering making solid colors
    return silf._new(im)

@app.route("/process_image")
def process_image():
    palette = [ 
        0,0,0,
        0,0,255,
        15,29,15,
        26,141,52,
        41,41,41,
        65,105,225,
        85,11,18,
        128,0,128,
        135,206,236,
        144,238,144,
        159,30,81,
        165,42,42,
        166,141,95,
        169,169,169,
        173,216,230,
        211,211,211,
        230,208,122,
        245,245,220,
        247,214,193,
        255,0,0,
        255,165,0,
        255,192,203,
        255,255,0,
        255,255,255
        ] + [0,] * 232 * 3

    files = random.choice(glob.glob("static/squares/*.jpg"))
    paletteImage = Image.new('P', (1, 1), 0)
    paletteImage.putpalette(palette)
    # open the source image
    imageOrginal = Image.open(files).convert('RGB')
    # convert it using our palette image
    cnt = random.randint(0,2000)
    imageCustomConvert = customConvert(imageOrginal, paletteImage,  dither=False).convert('RGB')
    processed_image = "static/processed/"+str(cnt)+"square_imageCustomConvert.jpg"
    imageCustomConvert.save(processed_image)
    return render_template('processed_image.html', processed_image=processed_image)
app.config['AUDIO_PATH'] = 'sample_data'
app.config['VIDEO_PATH'] = 'sample_data'
app.config['ALLOWED_EXTENSIONS'] = {'mp3', 'wav'}
app.config['CHECKPOINT_PATH'] = 'checkpoints/wav2lip_gan.pth'

@app.route('/create_avatar', methods=['GET', 'POST'])
def create_avatar():
    if request.method == 'POST':
        #check_point = os.path.join(app.config['CHECKPOINT_PATH'], 'checkpoints/wav2lip_gan.pth')
        check_point = 'checkpoints/wav2lip_gan.pth'
        wav_filename = os.path.join(app.config['AUDIO_PATH'], 'input_audio.wav')
        video_path = os.path.join(app.config['VIDEO_PATH'], 'input_video.mp4')
        logger.info(f'Video path: {video_path}')
        build_avatar = f"python inference.py --checkpoint_path {check_point} --face {video_path} --audio {wav_filename}"

        def generate_output():
            process = subprocess.Popen(build_avatar, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            for line in iter(process.stdout.readline, b''):
                yield line

        return Response(generate_output(), mimetype='text/plain')
    else:
        return render_template('create_avatar.html')
    
    
@app.route('/generate_vid', methods=['GET', 'POST'])
def generate_vid():
    current_datetime = datetime.now()
    str_current_datetime = str(current_datetime)
    logger.debug('Generating video', str_current_datetime)
    if request.method == 'POST':
        # Load the audio file
        audio_file = request.files['audio']
        filename = os.path.join(app.config['AUDIO_PATH'], 'input_audio.mp3')
        logger.info(f'Audio path: {filename}')
        audio_file.save(filename)

        # Get the duration of the audio using ffprobe
        command = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {filename}"
        duration = subprocess.check_output(command.split())
        duration = float(duration.strip().decode())
        logger.info(f'Duration: {duration}')
        # Load the image file
        image_file = request.files['image']
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image_file.filename))
        logger.info(f'Image path: {image_path}')
        image_file.save(image_path)

        # Create the video
        video_path = os.path.join(app.config['VIDEO_PATH'], 'input_video.mp4')
        logger.info(f'Video path: {video_path}')
        ffmpeg_command = f"ffmpeg -loop 1 -i {image_path} -c:v libx264 -t {duration+ 0.5} -pix_fmt yuv420p -y {video_path}"
        subprocess.run(ffmpeg_command, shell=True)

        return f'Video created: {video_path}'

    return render_template('generate_vid.html')

   
app.config['AUDIO_PATH'] = 'sample_data'
app.config['ALLOWED_EXTENSIONS'] = {'mp3'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
def convert_mp3_towav(mp3_filename, wav_filename):
    audio = AudioSegment.from_file(mp3_filename)
    audio.export(wav_filename, format='wav')
    
@app.route('/convert_audio', methods=['GET', 'POST'])
def convert_audio():
      if request.method == 'POST':
        mp3_filename = 'sample_data/input_audio.mp3'
        wav_filename = 'sample_data/input_audio.wav'
        convert_mp3_towav(mp3_filename, wav_filename)
        return f'Audio converted: {wav_filename}'
      return render_template('convert_audio.html')    
if __name__ == '__main__':
    app.run(debug=True)


