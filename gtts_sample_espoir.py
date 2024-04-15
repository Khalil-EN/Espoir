import os
import pygame
from gtts import gTTS

# Text to be converted to speech
text = "Hello, how are you today?"

# Create a gTTS object
tts = gTTS(text=text, lang='en')

# Save the speech to a file
output_file1 = "output1.mp3"
tts.save(output_file1)

# Check if the output file exists
if os.path.exists(output_file1):
    # Initialize the Pygame mixer
    pygame.mixer.init()

    # Load the output file
    pygame.mixer.music.load(output_file1)

    # Play the loaded file
    pygame.mixer.music.play()

    # Wait for the playback to finish
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)  # Adjust the tick rate as needed
else:
    print("Output file not found.")
