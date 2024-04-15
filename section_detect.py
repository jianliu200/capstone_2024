import gpiod
import time
import cv2
import torch
from picamera2 import Picamera2
from ultralytics import YOLO


LED_PIN1, LED_PIN2, LED_PIN3 = 9, 10, 11


chip = gpiod.Chip('gpiochip4')
RED = chip.get_line(LED_PIN1)
YELLOW = chip.get_line(LED_PIN2)
GREEN = chip.get_line(LED_PIN3)


RED.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
YELLOW.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
GREEN.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)


model = YOLO('yolov8n.pt')


piCam = Picamera2()
config = piCam.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"}, controls={"FrameRate": 30})
piCam.configure(config)
piCam.start()


x_line = 100


try:
    left_person_detected = False
    right_person_detected = False
    
    left_start_time = None
    right_start_time = None

    while True:
        frame = piCam.capture_array()
        results = model(frame, stream=True)

        left_class_counts = {}
        right_class_counts = {}

        # Get center line of frame
        x_middle = frame.shape[1] // 2
        cv2.line(frame, (x_middle, 0), (x_middle, frame.shape[0]), (255, 0, 0), 2)

        for result in results:
            for box in result.boxes:
                class_name = result.names[int(box.cls)]

                b = box.xyxy[0]
                x1, y1, x2, y2 = b
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                if x1 < x_middle:
                    left_class_counts[class_name] = left_class_counts.get(class_name, 0) + 1
                else:
                    right_class_counts[class_name] = right_class_counts.get(class_name, 0) + 1
                
                #cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)


        # PEOPLE ON STREET: RED
        if "person" in left_class_counts and left_class_counts["person"] > 0:
            if not left_person_detected:
                left_person_detected = True
                right_person_detected = False
                RED.set_value(1)
                YELLOW.set_value(0)
                GREEN.set_value(0)

        # PEOPLE WAITING ON SIDEWALK: YELLOW
        elif "person" in right_class_counts and right_class_counts["person"] > 0:
            if not right_person_detected:
                right_start_time = time.time()
                right_person_detected = True
                left_person_detected = False
            elif time.time() - right_start_time >= 1:  # Wait for 2 seconds before switching lights
                RED.set_value(0)
                YELLOW.set_value(1)
                GREEN.set_value(0)

        # NOBODY IN SIGHT: GREEN
        else:
            left_person_detected = False
            right_person_detected = False
            RED.set_value(0)
            YELLOW.set_value(0)
            GREEN.set_value(1)

        print(f'Detecting on the Left Side: {left_class_counts}')
        print(f'Detecting on the Right Side: {right_class_counts}')

        #cv2.imshow('YOLO Object Detection', frame)
        
       # if cv2.waitKey(1) == ord('q'):
        #    break

finally:
    cv2.destroyAllWindows()
    piCam.stop()

    RED.set_value(0)
    GREEN.set_value(0)
    YELLOW.set_value(0)
    RED.release()
    YELLOW.release()
    GREEN.release()
