from gtts import gTTS
import os
import pygame
import time
from gtts import gTTS
# Create a gTTS object and save it as an MP3 file
TEXT = "This is a quick test"
tts = gTTS(TEXT)
tts.save("Text01.mp3")
print(len(TEXT))
pygame.mixer.init()
pygame.mixer.music.load("Text0.mp3")
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    time.sleep(1)
