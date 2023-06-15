from flask import Flask, Response, render_template
import cv2
import numpy as np
import time

app = Flask(__name__)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    video = cv2.VideoCapture('path_to_your_video_file.mp4')
    text = "Your Very Long Text"
    font = cv2.FONT_HERSHEY_SIMPLEX
    position = (50, 50)
    font_scale = 1
    color = (0, 0, 255)
    thickness = 2

    # Calculate the text width to determine the scrolling distance
    text_width, _ = cv2.getTextSize(text, font, font_scale, thickness)[0]

    start_time = time.time()
    elapsed_time = 0

    while elapsed_time < 50:
        success, frame = video.read()
        if not success:
            break

        # Calculate the scrolling position based on elapsed time
        scroll_position = int((elapsed_time / 50) * text_width)

        # Create a black background for the marquee banner
        banner = np.zeros_like(frame)

        # Add the scrolling text to the marquee banner
        banner = cv2.putText(banner, text, (scroll_position, position[1]), font, font_scale, color, thickness, cv2.LINE_AA)

        # Combine the marquee banner with the original frame
        frame = cv2.add(frame, banner)

        # Convert the frame to JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        elapsed_time = time.time() - start_time

    video.release()

@app.route('/')
def marquis():
    return render_template('marquis.html')

if __name__ == '__main__':
    app.run()

