# Import OpenCV library
import cv2

# === Load the pre-trained Haar Cascade Face Detector ===
# This file contains the data to detect human faces
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# === Open the webcam (0 is the default camera) ===
camera = cv2.VideoCapture(0)

# === Keep running until we manually stop it ===
while True:
    # Read the current frame from the webcam
    success, frame = camera.read()

    # Convert the frame to grayscale (face detection works better on gray images)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale image
    faces = face_detector.detectMultiScale(
        gray_frame,      # Input image
        scaleFactor=1.1, # How much the image size is reduced at each image scale
        minNeighbors=4   # How many neighbors each candidate rectangle should have to retain it
    )

    # Draw a rectangle around each detected face
    for (x, y, width, height) in faces:
        cv2.rectangle(frame, (x, y), (x + width, y + height), color=(255, 0, 0), thickness=2)

    # Show the video with rectangles drawn
    cv2.imshow('🧠 Face Detection with OpenCV', frame)

    # If user presses 'q', break the loop and exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# === Cleanup: release the camera and close all OpenCV windows ===
camera.release()
cv2.destroyAllWindows()
