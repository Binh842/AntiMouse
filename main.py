import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import pyautogui as pg
import time
import math

FirstMove = True
virtual = None
def control_mouse(move,check_click,check_scroll):
    global FirstMove,virtual,click,scroll
    pg.FAILSAFE = False
    w, h = pg.size()
    if move and FirstMove:
        pre_x_virtual  = int(w * (1-move[0]))
        pre_y_virtual = int(h * move[1])
        virtual =[pre_x_virtual,pre_y_virtual]
        FirstMove = False
    if move and FirstMove == False:
        cur_x_virtual = int(w * (1-move[0]))
        cur_y_virtual = int(h * move[1])
        virtual.append(cur_x_virtual)
        virtual.append(cur_y_virtual)

        pre_x_real = pg.position()[0]
        pre_y_real = pg.position()[1]

        if virtual[2] > virtual[0]:         
            cur_x_real = pre_x_real + (virtual[2] - virtual[0]) 
        else:
            cur_x_real = pre_x_real - (virtual[0] - virtual[2]) 
        if virtual[3] > virtual[1]:   
            cur_y_real = pre_y_real + (virtual[3] - virtual[1])
        else:
            cur_y_real = pre_y_real - (virtual[1] - virtual[3]) 
       
        if cur_x_real > w:
            cur_x_real = w 
        elif cur_x_real < 0:
            cur_x_real =0
        if cur_y_real > h:
            cur_y_real = h 
        elif cur_y_real < 0:
            cur_y_real = 0
        # distance = math.sqrt((cur_x-x)**2 + (cur_y-y)**2)
        pg.moveTo(cur_x_real,cur_y_real,duration=0.05,tween=pg.easeInOutQuad)
        virtual.pop(0)
        virtual.pop(0)
    if move == []:
        FirstMove = True
        virtual = None
    if check_click:
        if 'left' in check_click:
            pg.click(button='left')
        if 'right' in check_click:
            pg.click(button='right')
        click = []
    if  len(check_scroll) == 2 :
        if check_scroll[0] < check_scroll[1]:
            pg.scroll(-1)
        else:
            pg.scroll(1)
        scroll.pop(0)

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

hand_name = []
hand_coordinates_move = []
click = []
scroll = [0]
off  = False
def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):    
    global hand_name, hand_coordinates_move,click,scroll,off
    hand_name = []
    if result.handedness:    
        # print(result.handedness)  
        for i in  range(len(result.handedness)):           
            hand_name.append(result.handedness[i][0].category_name)  
            if result.gestures:
                hand_name.append(result.gestures[i][0].category_name)
                
    hand_coordinates_move = []
    if result.hand_landmarks and result.gestures[0][0].category_name == 'one':
        hand_coordinates_move.append(result.hand_landmarks[0][8].x)
        hand_coordinates_move.append(result.hand_landmarks[0][8].y)
    if  result.hand_landmarks and result.gestures[0][0].category_name == 'two_up' :
        click.append('left')
    if  result.hand_landmarks and result.gestures[0][0].category_name == 'two_up_inv' :
        click.append('right')
    if  result.hand_landmarks and result.gestures[0][0].category_name == 'fist' :
        scroll.append(result.hand_landmarks[0][9].y)
    if  result.hand_landmarks and result.gestures[0][0].category_name == 'stop' :
        if 'Left' in hand_name:
            off = True
 
model_path = 'gesture_recognizer.task'

num_hands = 2

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    num_hands = num_hands,
    result_callback=print_result)

frame_timestamp_ms = 1

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=num_hands,
        min_detection_confidence=0.65,
        min_tracking_confidence=0.65)

def show_hand_name(frame):
    y,x,_ = frame.shape
    
    #  thckness for all\
    thickness = -1

    #  Hand Left
    start_point = (0, 0) 
    end_point = (100, 50) 
    color = (9, 0, 255) 
    cv2.rectangle(frame, start_point, end_point, color, thickness) 

    # Gestures Left
    start_point = (101, 0) 
    end_point = (290, 50) 
    color = (255, 0, 255) 
    cv2.rectangle(frame, start_point, end_point, color, thickness) 

    # Hand Right
    start_point = (x-100, 0) 
    end_point = (x, 50) 
    color = (9, 0, 255) 
    cv2.rectangle(frame, start_point, end_point, color, thickness) 

    #  Gestures Right
    start_point = (x-100-190, 0) 
    end_point = (x-101, 50) 
    color = (255, 0, 255) 
    cv2.rectangle(frame, start_point, end_point, color, thickness) 

    for i in range(len(hand_name)-1):
        if hand_name[i] == 'Left' :
            text = "Left"
            org  = (20,35)
            fontFace = cv2.FONT_HERSHEY_SIMPLEX 
            fontScale = 1
            color = (0, 255, 0) 
            thickness = 2
            frame = cv2.putText(frame, text = text, org = org, fontFace = fontFace, 
                                fontScale = fontScale, color = color , thickness = thickness)
            
            org  = (105,35)
            fontFace = cv2.FONT_HERSHEY_SIMPLEX 
            fontScale = 1
            color = (0, 255, 0) 
            thickness = 2
            text = hand_name[i+1]
            frame = cv2.putText(frame, text = text, org = org, fontFace = fontFace, 
                                fontScale = fontScale, color = color , thickness = thickness)

        if hand_name[i] == 'Right':
            text = 'Right'
            org  = (x- 85,35)
            fontFace = cv2.FONT_HERSHEY_SIMPLEX 
            fontScale = 1
            color = (0, 255, 0) 
            thickness = 2
            frame = cv2.putText(frame, text = text, org = org, fontFace = fontFace, 
                                fontScale = fontScale, color = color , thickness = thickness)
            
            text = hand_name[i+1]
            org  = (x - 291,35)
            fontFace = cv2.FONT_HERSHEY_SIMPLEX 
            fontScale = 1
            color = (0, 255, 0) 
            thickness = 2
            frame = cv2.putText(frame, text = text, org = org, fontFace = fontFace, 
                                fontScale = fontScale, color = color , thickness = thickness)


    return frame
cap = cv2.VideoCapture(0)
with GestureRecognizer.create_from_options(options) as recognizer:
    frame_count = 0
    start_time = time.time()
    while True:
        ret, frame = cap.read()
        if ret:
            numpy_frame_from_opencv = frame
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_frame_from_opencv)

            results = hands.process(frame)

            if results.multi_hand_landmarks:
                for detection in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame,detection, mp_hands.HAND_CONNECTIONS,
                                            mp_drawing.DrawingSpec(color=(255,255,102), thickness=2, circle_radius=2),
                                            mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))
                
            recognizer.recognize_async(mp_image, frame_timestamp_ms)
            frame_timestamp_ms +=1 

            frame = show_hand_name(frame)
            control_mouse(hand_coordinates_move,click,scroll)

            # fps
            frame_count += 1
            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time
            cv2.putText(frame, f"FPS: {fps:.0f}", (1, 465), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.imshow('Hand landmark detection', frame)
            
        if cv2.waitKey(1) == ord('q') or off == True:
            break  
        
cap.release()
cv2.destroyAllWindows()
