#!venv/bin/python
# ---------- playmp3.py ----------------
from gtts import gTTS
import os
import pygame
# Create a gTTS object and save it as an MP3 file
#TEXT = "This is a quick test"
#tts = gTTS(TEXT)
#tts.save("Text0.mp3")
#print(len(TEXT))
pygame.mixer.init()
pygame.mixer.music.load("Text0.mp3")
pygame.mixer.music.play()
