import mediapipe as mp


class HandDetect():

    def __init__(self, model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=2):
        
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(model_complexity = model_complexity , min_detection_confidence = min_detection_confidence, min_tracking_confidence = min_tracking_confidence, max_num_hands = max_num_hands)


    def detection_hand(self, img):

        results = self.hands.process(img)

        posList = []

        posList_nolabel = []

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for label, pos in enumerate(hand_landmarks.landmark):

                    h, w, p = img.shape
                    cx, cy = int(pos.x * w), int(pos.y * h)
                    
                    posList.append([label, cx, cy])
                    
                    posList_nolabel.append([cx, cy])

                    self.mp_drawing.draw_landmarks(
                        img,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style())
        
        return img, posList, posList_nolabel