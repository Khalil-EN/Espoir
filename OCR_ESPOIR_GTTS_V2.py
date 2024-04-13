import pytesseract
import cv2
import speech_recognition as sr
import pyttsx3
import os
import numpy as np
import pyaudio
import wave
from pydub import AudioSegment
from openai import OpenAI
from gtts import gTTS








# Initialize webcam
webcam = cv2.VideoCapture(0)

client = OpenAI(api_key = 'yourkey')



def get_transcription_from_whisper():


    # Set the audio parameters
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 2048
    SILENCE_THRESHOLD = 300  # Silence threshold
    SPEECH_END_TIME = 1.0  # Time of silence to mark the end of speech

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Recording...Waiting for speech to begin.")

    frames = []
    silence_frames = 0
    is_speaking = False
    total_frames = 0

    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        total_frames += 1

        # Convert audio chunks to integers
        audio_data = np.frombuffer(data, dtype=np.int16)

        # Check if user has started speaking
        if np.abs(audio_data).mean() > SILENCE_THRESHOLD:
            is_speaking = True

        # Detect if the audio chunk is silence
        if is_speaking:
            if np.abs(audio_data).mean() < SILENCE_THRESHOLD:
                silence_frames += 1
            else:
                silence_frames = 0

        # End of speech detected
        if is_speaking and silence_frames > SPEECH_END_TIME * (RATE / CHUNK):
            print("End of speech detected.")
            break

    # Stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    print("Finished recording.")
    combined_audio_data = b''.join(frames)

    # Convert raw data to an AudioSegment object
    audio_segment = AudioSegment(
        data=combined_audio_data,
        sample_width=audio.get_sample_size(FORMAT),
        frame_rate=RATE,
        channels=CHANNELS
    )

    # Export as a compressed MP3 file with a specific bitrate
    audio_segment.export("output_audio_file.mp3", format="mp3", bitrate="32k")

    audio_file = open("output_audio_file.mp3", "rb")
    transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file
    )
    # Return the transcript text
    return transcript.text





while True:
    try:
        # Capture frame from webcam
        check, frame = webcam.read()
        cv2.imshow("Capturing", frame)

        # Recognize speech
        words = get_transcription_from_whisper()
        print("Recognized:", words)

        # Check for wake word or key press
        if "blind" in words.lower()  or cv2.waitKey(1) & 0xFF == ord('z'):
            # Save captured image
            cv2.imwrite(filename='saved_img.jpg', img=frame)
            print("Image saved!")

            text = "هل أنت في حاجة إلى اللغة العربية أم لغة أجنبية؟"
            tts_arabic2=gTTS(text=text, lang='ar')
            tts_arabic2.save("output_arabic2.mp3")
            os.system("start output_arabic2.mp3")

            response=get_transcription_from_whisper()
            print("Recognized:", response)
            if response=="العربية":
                # Perform OCR on the saved image
                img = cv2.imread('saved_img.jpg')
                string = pytesseract.image_to_string(img, lang='ara')
                print("OCR Result:", string)
                tts_arabic = gTTS(text=string, lang='ar')
                tts_arabic.save("output_arabic.mp3")
                os.system("start output_arabic.mp3")
            else:
                # Perform OCR on the saved image
                img = cv2.imread('saved_img.jpg')
                string = pytesseract.image_to_string(img)
                print("OCR Result:", string)
            # Speak the OCR result
                tts_english = gTTS(text=string, lang='en')

# Save the speech to a file
                tts_english.save("output_english.mp3")

# Play the speech using the default audio player
                os.system("start output_english.mp3")

            #break

    except sr.UnknownValueError:
        print("Speech recognition could not understand audio.")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    except cv2.error as e:
        print("Error capturing image from webcam:", e)
    except Exception as e:
        print("An error occurred:", e)
        break

# Release resources
webcam.release()
cv2.destroyAllWindows()
