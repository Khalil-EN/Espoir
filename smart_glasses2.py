import pytesseract
import cv2
import speech_recognition as sr
import pyttsx3

# Initialize speech recognition
r = sr.Recognizer()
mic = sr.Microphone()

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 100)
engine.setProperty('voice', 'english')

# Initialize webcam
webcam = cv2.VideoCapture(0)

def recognize_speech():
    with mic as source:
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=3)
            return r.recognize_google(audio)
        except sr.WaitTimeoutError:
            print("No speech detected within the timeout period.")
            return ""

while True:
    try:
        # Capture frame from webcam
        check, frame = webcam.read()
        cv2.imshow("Capturing", frame)

        # Recognize speech
        words = recognize_speech()
        print("Recognized:", words)

        # Check for wake word or key press
        if words.lower() == "blind" or cv2.waitKey(1) & 0xFF == ord('z'):
            # Save captured image
            cv2.imwrite(filename='saved_img.jpg', img=frame)
            print("Image saved!")

            # Perform OCR on the saved image
            img = cv2.imread('saved_img.jpg')
            string = pytesseract.image_to_string(img)
            print("OCR Result:", string)

            # Speak the OCR result
            engine.say(string)
            engine.runAndWait()

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
