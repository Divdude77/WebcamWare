import cv2
import mediapipe as mp
import math

class WebCam():
    _instance = None
    _initialized = False

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(WebCam, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.cap = None
            self._initialized = True
    
    def startWebcam(self):
        if not self.cap:
            self.cap = cv2.VideoCapture(1)
    
    def stopWebcam(self):
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def returnFrame(self):
        if not self.cap:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None

        return frame


class PoseEstimator():
    _instance = None
    _initialized = False

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(PoseEstimator, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose()
            self._initialized = True

    def getPoints(self, frame, points_to_display=list(range(0, 33))) -> dict:
        pose_results = self.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if pose_results.pose_landmarks:
            landmarks_to_display = dict.fromkeys(points_to_display, None)

            for idx in landmarks_to_display:
                landmark_point = pose_results.pose_landmarks.landmark[idx]
                landmark_point.x = 1 - landmark_point.x
                landmarks_to_display[idx] = landmark_point
            
            return landmarks_to_display
    
    def pointsVisible(self, points_read, points_to_check) -> bool:
        if not points_to_check:
            return True

        for idx in points_read:
            landmark = points_read[idx]
            if landmark.visibility < 0.5:
                return False
        
        return True

    def getAngle(self, points_read, point1, point2, point3) -> float:
        if not points_read:
            return None
        
        point1 = points_read.get(point1, None)
        point2 = points_read.get(point2, None)
        point3 = points_read.get(point3, None)

        if not point1 or not point2 or not point3:
            return None
        
        angle = math.degrees(math.atan2(point3.y - point2.y, point3.x - point2.x) - math.atan2(point1.y - point2.y, point1.x - point2.x))

        if angle < 0:
            angle = 360 + angle

        return angle


class HandEstimator():
    _instance = None
    _initialized = False

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(HandEstimator, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands()
            self._initialized = True

    # For all below methods:
    #   n = 0 -> left
    #   n = 1 -> right
    #   n = 2 -> both
    
    def getPoints(self, frame, points_to_display=list(range(0, 21)), n=2) -> list:
        hand_results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if hand_results.multi_hand_landmarks:
            hands = []
            for landmarks, hand_info in zip(hand_results.multi_hand_landmarks, hand_results.multi_handedness):
                landmarks_to_display = dict.fromkeys(points_to_display, None)

                for idx in landmarks_to_display:
                    landmark_point = landmarks.landmark[idx]
                    landmark_point.x = 1 - landmark_point.x
                    landmarks_to_display[idx] = landmark_point
                
                if n == 0 and hand_info.classification[0].label == "Right":
                    return ["left", landmarks_to_display]
                elif n == 1 and hand_info.classification[0].label == "Left":
                    return ["right", landmarks_to_display]
                elif n == 2:
                    hands.append(["left" if hand_info.classification[0].label == "Right" else "right", landmarks_to_display])

            return hands

    def pointsVisible(self, frame, points, n=2) -> bool:
        if not points:
            return True
        
        landmarks = self.getPoints(frame, points)

        if landmarks:
            c = 0

            for i in landmarks:
                if i[0] == "left" and n == 0:
                    return True
                if i[0] == "right" and n == 1:
                    return True
                c += 1

            if n == 2 and c == 2:
                    return True

        return False
    
    def isHandOpen(self, frame, n=2) -> bool:
        if n == 2:
            return self.isHandOpen(frame, 0) and self.isHandOpen(frame, 1)

        hand = self.getPoints(frame, [5, 8, 9, 12, 13, 16, 17, 20], n)
        if hand:
            hand = hand[1]
            if hand[4].y < hand[0].y and hand[8].y < hand[5].y and hand[12].y < hand[9].y and hand[16].y < hand[13].y and hand[20].y < hand[17].y:
                return True
        
        return False

    def isFist(self, frame, n=2) -> bool:
        if n == 2:
            return self.isFist(frame, 0) and self.isFist(frame, 1)

        hand = self.getPoints(frame, [0, 4, 5, 8, 9, 12, 13, 16, 17, 20], n)
        if hand:
            hand = hand[1]
            if hand[8].y > hand[5].y and hand[12].y > hand[9].y and hand[16].y > hand[13].y and hand[20].y > hand[17].y:
                return True
        
        return False


if __name__ == "__main__":
    wc1 = WebCam()
    pe = PoseEstimator()
    he = HandEstimator()
    wc1.startWebcam()

    wc = WebCam()

    while True:
        frame = wc.returnFrame()

        print(he.isFist(frame, 2))
        # hands = he.getPoints(frame)
        # pose = pe.getPoints(frame)

        # if hands:
        #     for hand in hands:
        #         landmarks = hand[2]
        #         hand_type = hand[0]
        #         for idx in landmarks:
        #             landmark = landmarks[idx]
        #             cv2.circle(frame, (int((1 - landmark.x) * frame.shape[1]), int(landmark.y * frame.shape[0])), 5, (0, 0, 255), -1)

        # if pose:
        #     for idx in pose:
        #         landmark = pose[idx]
        #         if landmark.visibility > 0.5:
        #             cv2.circle(frame, (int((1 - landmark.x) * frame.shape[1]), int(landmark.y * frame.shape[0])), 5, (0, 0, 255), -1)

        cv2.imshow('Pose and Hand Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    wc.stopWebcam()
    cv2.destroyAllWindows()