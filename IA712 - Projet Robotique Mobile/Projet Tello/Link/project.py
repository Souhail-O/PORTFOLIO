import time
import socket
from djitellopy import Tello
import mediapipe as mp
import cv2

# see: https://github.com/damiafuentes/DJITelloPy
# see: https://google.github.io/mediapipe/getting_started/python


# Instantiate Tello object
print("Create Tello object")
tello = Tello()

# Connect to the drone
print("Connect to Tello Drone")
tello.connect()

print(f"Battery Life Pecentage: {tello.get_battery()}")

##tello.stream_on??

print("Takeoff - hoser!")
tello.takeoff()

time.sleep(1)
print("Move Left X cm")
#tello.move_left(50)

time.sleep(5)
#print("Rotate clockwise")
#tello.rotate_clockwise(90)

time.sleep(1)
#print("Move forward X cm")
#tello.move_forward(50)
""

##mp_drawing = mp.solutions.drawing_utils
##mp_drawing_styles = mp.solutions.drawing_styles
#mp_hands = mp.solutions.hands
print('Stream On')
tello.stream_on()
time.sleep(5)
# For static images:
"""
IMAGE_FILES = []
with mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=2,
    min_detection_confidence=0.5) as hands:
  for idx, file in enumerate(IMAGE_FILES):
    # Read an image, flip it around y-axis for correct handedness output (see
    # above).
    image = cv2.flip(cv2.imread(file), 1)
    # Convert the BGR image to RGB before processing.
    results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Print handedness and draw hand landmarks on the image.
    print('Handedness:', results.multi_handedness)
    if not results.multi_hand_landmarks:
      continue
    image_height, image_width, _ = image.shape
    annotated_image = image.copy()
    for hand_landmarks in results.multi_hand_landmarks:
      print('hand_landmarks:', hand_landmarks)
      print(
          f'Index finger tip coordinates: (',
          f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width}, '
          f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height})'
      )
      mp_drawing.draw_landmarks(
          annotated_image,
          hand_landmarks,
          mp_hands.HAND_CONNECTIONS,
          mp_drawing_styles.get_default_hand_landmarks_style(),
          mp_drawing_styles.get_default_hand_connections_style())
    cv2.imwrite(
        '/tmp/annotated_image' + str(idx) + '.png', cv2.flip(annotated_image, 1))
    # Draw hand world landmarks.
    if not results.multi_hand_world_landmarks:
      continue
    for hand_world_landmarks in results.multi_hand_world_landmarks:
      mp_drawing.plot_landmarks(
        hand_world_landmarks, mp_hands.HAND_CONNECTIONS, azimuth=5)"""




print("Prepare floor to land.... you have 5 second")
#time.sleep(5)

print("landing")
tello.land()
print("touchdown.... goodbye")

