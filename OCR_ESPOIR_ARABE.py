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
import azure.cognitiveservices.speech as speechsdk
import xml.etree.ElementTree as ET



speech_key = "65469d8fa0b345029c9cdcae267bbb06"
service_region = "westeurope"

speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Initialize webcam
webcam = cv2.VideoCapture(0)

client = OpenAI(api_key = 'code')#code=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



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




def generate_audio(text, output_file, language="ar-SA", voice_name="ar-SA-HamedNeural"):
    try:


        # Create the speech synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

        # Create SSML string with the specified text, language, and voice
        ssml = f"""
        <speak version="1.0" xml:lang="{language}" xmlns="http://www.w3.org/2001/10/synthesis"
        xmlns:mstts="https://www.w3.org/2001/mstts">
            <voice name="{voice_name}">
                <mstts:express-as style="default">
                    <prosody rate="1.0">
                        {text}
                    </prosody>
                </mstts:express-as>
            </voice>
        </speak>
        """

        # Create an SSML speech synthesis result
        result = synthesizer.speak_ssml(ssml)

        # Save the synthesized speech to a WAV file
        with open(output_file, "wb") as audio_file:
            result.streams[0].stream.readinto(audio_file)
    except AttributeError as e:
        # Handle the error gracefully
        print("An error occurred:", e)
        print("Failed to generate audio. Please check the input text and try again.")
        # Perform any necessary cleanup or provide fallback behavior



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
            output_file = "arabic_audio.wav"
            generate_audio(text, output_file)

            response=get_transcription_from_whisper()
            print("Recognized:", response)
            if response=="العربية":
                # Perform OCR on the saved image
                img = cv2.imread('saved_img.jpg')
                string = pytesseract.image_to_string(img, lang='ara')
                print("OCR Result:", string)
                output_file = "arabic_audio.wav"
                generate_audio(string, output_file)
            else:
                # Perform OCR on the saved image
                img = cv2.imread('saved_img.jpg')
                string = pytesseract.image_to_string(img)
                print("OCR Result:", string)
            # Speak the OCR result
                output_file = "english_audio.awv"
                generate_audio(string, output_file, language="en-US", voice_name="en-US-GuyNeural")

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
