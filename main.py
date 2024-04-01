import time
import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import Tracker
import math
import pyautogui

# Getting screen resolution
w, h = pyautogui.size()
width, height = w*3, h*3
# width, height = 1366, 768

# class_list = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
#               'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
#               'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
#               'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
#               'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
#               'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
#               'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard',
#               'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
#               'teddy bear', 'hair drier', 'toothbrush']
class_list = ['drone']

model = YOLO('drone.pt')
print(model.names)
tracker = Tracker()

# cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('highway_mini.mp4')
camera1 = cv2.VideoCapture('drone.mkv')
camera2 = cv2.VideoCapture('drone.mkv')
camera3 = cv2.VideoCapture('drone.mkv')

if not camera1.isOpened():
    print("Error1")
if not camera2.isOpened():
    print("Error2")
if not camera3.isOpened():
    print("Error2")
left1 = {}
right1 = {}
left2 = {}
right2 = {}
left3 = {}
right3 = {}
counter_down = []
counter_up = []

red_line_x1 = math.floor(width / 9)
blue_line_x1 = math.floor((width / 9)*2)
red_line_x2 = math.floor(width / 9)*4
blue_line_x2 = math.floor((width / 9)*5)
red_line_x3 = math.floor(width / 9)*7
blue_line_x3 = math.floor((width / 9)*8)
offset = 6

while True:
    # ret, frame = cap.read()
    # if not ret:
    #     break
    # count += 1
    # # if count % 2 != 0:
    # #     continue
    # frame = cv2.resize(frame, (1020, 500))
    _, frame1 = camera1.read()
    _, frame2 = camera2.read()
    _, frame3 = camera3.read()

    frame1 = cv2.resize(frame1, (math.floor(width / 3), math.floor(height / 3)))
    frame2 = cv2.resize(frame2, (math.floor(width / 3), math.floor(height / 3)))
    frame3 = cv2.resize(frame3, (math.floor(width / 3), math.floor(height / 3)))

    frame = cv2.hconcat([frame1, frame2, frame3])

    results = model.predict(frame)
    a = results[0].boxes.data
    a = a.detach().cpu().numpy()
    px = pd.DataFrame(a).astype("float")
    print(px)
    list1 = []

    for index, row in px.iterrows():
        x1 = int(row[0])
        y1 = int(row[1])
        x2 = int(row[2])
        y2 = int(row[3])
        d = int(row[5])
        c = class_list[d]
        if 'drone' in c:
            list1.append([x1, y1, x2, y2])

    bbox_id = tracker.update(list1)
    for bbox in bbox_id:
        x3, y3, x4, y4, id1 = bbox
        cx = int(x3 + x4) // 2
        cy = int(y3 + y4) // 2

        area = (x4 - x3) - (y4 - y3)
        if area == 0:
            area = 1
        distance2 = round((62500 / area) / 1000, 2)
        # print distance of drone from camera
        cv2.putText(frame, str(distance2) + 'm', (x3, y4), cv2.FONT_HERSHEY_COMPLEX, 0.3, (255, 255, 255), 1)

        # print position of drone according to Sectors
        if cx < 250:
            cv2.putText(frame, str('Sector 1'), (x4, y3), cv2.FONT_HERSHEY_COMPLEX, 0.3, (255, 255, 0), 1)
        elif 250 < cx < 500:
            cv2.putText(frame, str('Sector 2'), (x4, y3), cv2.FONT_HERSHEY_COMPLEX, 0.3, (255, 255, 0), 1)
        elif 500 < cx < 750:
            cv2.putText(frame, str('Sector 3'), (x4, y3), cv2.FONT_HERSHEY_COMPLEX, 0.3, (255, 255, 0), 1)
        elif 750 < cx < 1000:
            cv2.putText(frame, str('Sector 4'), (x4, y3), cv2.FONT_HERSHEY_COMPLEX, 0.3, (255, 255, 0), 1)
        elif 1000 < cx < 1250:
            cv2.putText(frame, str('Sector 5'), (x4, y3), cv2.FONT_HERSHEY_COMPLEX, 0.3, (255, 255, 0), 1)
        else:
            cv2.putText(frame, str('Sector 6'), (x4, y3), cv2.FONT_HERSHEY_COMPLEX, 0.3, (255, 255, 0), 1)

        # calculating the speed of drone in camera 1 from left to right
        if (cx + offset) > red_line_x1 > (cx - offset):
            left1[id1] = time.time()  # current time when drone touch the first line
        if id1 in left1:
            if (cx + offset) > blue_line_x1 > (cx - offset):
                elapsed_time = time.time() - left1[id1]  # current time when vehicle touch the second line. Also we a
                # re minuting the previous time ( current time of line 1)
                if counter_down.count(id1) == 0:
                    counter_down.append(id1)
                    distance = 10  # meters - distance between the 2 lines is 10 meters
                    a_speed_ms = distance / elapsed_time
                    a_speed_kh = a_speed_ms * 3.6  # this will give kilometers per hour for each vehicle. This is the
                    cv2.circle(frame, (cx, cy), 4, (0, 0, 255), 1)
                    cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)  # Draw bounding box
                    cv2.putText(frame, str(id1), (x3, y3), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(frame, str(int(a_speed_kh)) + 'Km/h', (x4, y4), cv2.FONT_HERSHEY_COMPLEX, 0.8,
                                (0, 255, 255), 2)

        # going right to left
        if (cx + offset) > blue_line_x1 > (cx - offset):
            right1[id1] = time.time()
        if id1 in right1:

            if (cx + offset) > red_line_x1 > (cx - offset):
                elapsed1_time = time.time() - right1[id1]
                # formula of speed= distance/time  (distance travelled and elapsed time) Elapsed time is It
                # represents the duration between the starting point and the ending point of the movement.
                if counter_up.count(id1) == 0:
                    counter_up.append(id1)
                    distance = 10  # meters  (Distance between the 2 lines is 10 meters )
                    a_speed_ms1 = distance / elapsed1_time
                    a_speed_kh1 = a_speed_ms1 * 3.6
                    cv2.circle(frame, (cx, cy), 4, (0, 0, 255), 1)
                    cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)  # Draw bounding box
                    cv2.putText(frame, str(id1), (x3, y3), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(frame, str(int(a_speed_kh1)) + 'Km/h', (x4, y4), cv2.FONT_HERSHEY_COMPLEX, 0.8,
                                (0, 255, 255), 2)

        # calculating the speed of drone in camera 3 from left to right
        if (cx + offset) > red_line_x2 > (cx - offset):
            left2[id1] = time.time()  # current time when drone touch the first line
        if id1 in left2:
            if (cx + offset) > blue_line_x2 > (cx - offset):
                elapsed_time = time.time() - left2[id1]  # current time when vehicle touch the second line. Also we a
                # re minuting the previous time ( current time of line 1)
                if counter_down.count(id1) == 0:
                    counter_down.append(id1)
                    distance = 10  # meters - distance between the 2 lines is 10 meters
                    a_speed_ms = distance / elapsed_time
                    a_speed_kh = a_speed_ms * 3.6  # this will give kilometers per hour for each vehicle. This is the
                    cv2.circle(frame, (cx, cy), 4, (0, 0, 255), 1)
                    cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)  # Draw bounding box
                    cv2.putText(frame, str(id1), (x3, y3), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(frame, str(int(a_speed_kh)) + 'Km/h', (x4, y4), cv2.FONT_HERSHEY_COMPLEX, 0.8,
                                (0, 255, 255), 2)

        # going right to left
        if (cx + offset) > blue_line_x2 > (cx - offset):
            right2[id1] = time.time()
        if id1 in right2:

            if (cx + offset) > red_line_x2 > (cx - offset):
                elapsed1_time = time.time() - right2[id1]
                # formula of speed= distance/time  (distance travelled and elapsed time) Elapsed time is It
                # represents the duration between the starting point and the ending point of the movement.
                if counter_up.count(id1) == 0:
                    counter_up.append(id1)
                    distance = 10  # meters  (Distance between the 2 lines is 10 meters )
                    a_speed_ms1 = distance / elapsed1_time
                    a_speed_kh1 = a_speed_ms1 * 3.6
                    cv2.circle(frame, (cx, cy), 4, (0, 0, 255), 1)
                    cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)  # Draw bounding box
                    cv2.putText(frame, str(id1), (x3, y3), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(frame, str(int(a_speed_kh1)) + 'Km/h', (x4, y4), cv2.FONT_HERSHEY_COMPLEX, 0.8,
                                (0, 255, 255), 2)

        # calculating the speed of drone in camera 3 from left to right
        if (cx + offset) > red_line_x3 > (cx - offset):
            left3[id1] = time.time()  # current time when drone touch the first line
        if id1 in left3:
            if (cx + offset) > blue_line_x3 > (cx - offset):
                elapsed_time = time.time() - left3[id1]  # current time when vehicle touch the second line. Also we a
                # re minuting the previous time ( current time of line 1)
                if counter_down.count(id1) == 0:
                    counter_down.append(id1)
                    distance = 10  # meters - distance between the 2 lines is 10 meters
                    a_speed_ms = distance / elapsed_time
                    a_speed_kh = a_speed_ms * 3.6  # this will give kilometers per hour for each vehicle. This is the
                    cv2.circle(frame, (cx, cy), 4, (0, 0, 255), 1)
                    cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)  # Draw bounding box
                    cv2.putText(frame, str(id1), (x3, y3), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(frame, str(int(a_speed_kh)) + 'Km/h', (x4, y4), cv2.FONT_HERSHEY_COMPLEX, 0.8,
                                (0, 255, 255), 2)

        # going right to left
        if (cx + offset) > blue_line_x3 > (cx - offset):
            right3[id1] = time.time()
        if id1 in right3:

            if (cx + offset) > red_line_x3 > (cx - offset):
                elapsed1_time = time.time() - right3[id1]
                # formula of speed= distance/time  (distance travelled and elapsed time) Elapsed time is It
                # represents the duration between the starting point and the ending point of the movement.
                if counter_up.count(id1) == 0:
                    counter_up.append(id1)
                    distance = 10  # meters  (Distance between the 2 lines is 10 meters )
                    a_speed_ms1 = distance / elapsed1_time
                    a_speed_kh1 = a_speed_ms1 * 3.6
                    cv2.circle(frame, (cx, cy), 4, (0, 0, 255), 1)
                    cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)  # Draw bounding box
                    cv2.putText(frame, str(id1), (x3, y3), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(frame, str(int(a_speed_kh1)) + 'Km/h', (x4, y4), cv2.FONT_HERSHEY_COMPLEX, 0.8,
                                (0, 255, 255), 2)

    text_color = (0, 0, 0)  # Black color for text
    yellow_color = (0, 255, 255)  # Yellow color for background
    red_color = (0, 0, 255)  # Red color for lines
    blue_color = (255, 0, 0)  # Blue color for lines

    cv2.line(frame, (math.floor(width / 9), height - 10), (math.floor(width / 9), 10), red_color, 2)
    cv2.putText(frame, 'Red Line1', (math.floor(width / 9), height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1,
                cv2.LINE_AA)

    cv2.line(frame, (math.floor(width / 9) * 2, height - 10), (math.floor(width / 9) * 2, 10), blue_color, 2)
    cv2.putText(frame, 'Blue Line1', (math.floor(width / 9) * 2, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                text_color, 1, cv2.LINE_AA)

    cv2.line(frame, (math.floor(width / 9) * 4, height - 10), (math.floor(width / 9) * 4, 10), red_color, 2)
    cv2.putText(frame, 'Red Line2', (math.floor(width / 9) * 4, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color,
                1, cv2.LINE_AA)

    cv2.line(frame, (math.floor(width / 9) * 5, height - 10), (math.floor(width / 9) * 5, 10), blue_color, 2)
    cv2.putText(frame, 'Blue Line2', (math.floor(width / 9) * 5, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                text_color, 1, cv2.LINE_AA)

    cv2.line(frame, (math.floor(width / 9) * 7, height - 10), (math.floor(width / 9) * 7, 10), red_color, 2)
    cv2.putText(frame, 'Red Line3', (math.floor(width / 9) * 7, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color,
                1, cv2.LINE_AA)

    cv2.line(frame, (math.floor(width / 9) * 8, height - 10), (math.floor(width / 9) * 8, 10), blue_color, 2)
    cv2.putText(frame, 'Blue Line3', (math.floor(width / 9) * 8, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                text_color, 1, cv2.LINE_AA)

    # cv2.putText(frame, ('Going Down - ' + str(len(counter_down))), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
    # text_color, 1, cv2.LINE_AA) cv2.putText(frame, ('Going Up - ' + str(len(counter_up))), (10, 60),
    # cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

    cv2.imshow("frames", frame)
    if cv2.waitKey(0) & 0xFF == 27:
        break

# cap.release()
# out.release()
# cv2.destroyAllWindows()
