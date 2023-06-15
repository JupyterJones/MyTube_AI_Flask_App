from flask import Flask, send_file
from moviepy.editor import ImageSequenceClip

app = Flask(__name__)

@app.route('/')
def generate_blank_video():
    blank_image = (255 * np.ones((512, 1024, 3))).astype(np.uint8)
    clip = ImageSequenceClip([blank_image], fps=24)
    output_path = 'blank_video.mp4'
    clip.write_videofile(output_path, codec='libx264')
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run()
