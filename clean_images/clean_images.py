import os
import shutil
import logging
def clean_images():
    # Define the source and destination directories
    src_dir = '/home/jack/Desktop/FLASK/static/images/uploads'
    dest_dir = '/home/jack/Desktop/FLASK/static/images/cleaned'

    # Make sure the destination directory exists
    os.makedirs(dest_dir, exist_ok=True)

    # Loop over all the files in the source directory
    for filename in os.listdir(src_dir):
        # Check if the file is a JPG image
        if filename.lower().endswith('XXXC.jpg'):
            # Generate the full path to the source and destination files
            src_path = os.path.join(src_dir, filename)
            dest_path = os.path.join(dest_dir, filename)
            print("src_path, dest_path",src_path, dest_path)
            # Move the file from the source directory to the destination directory
            #shutil.move(src_path, dest_path)

    # Print a message to indicate the function has finished
    print('All JPG images have been moved to the cleaned directory.')

