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

try:
    person_detected = False
    start_time = None

    while True:
        frame = piCam.capture_array()
        results = model(frame, stream=True)

        class_counts = {}

        for result in results:
            for box in result.boxes:
                class_name = result.names[int(box.cls)]
                class_counts[class_name] = class_counts.get(class_name, 0) + 1

        print(f'Detecting: {class_counts}')

        if "person" in class_counts and class_counts["person"] > 0:
            if not person_detected:
                start_time = time.time()
                person_detected = True
            elif time.time() - start_time >= 3:  # Wait for 3 seconds before switching lights
                RED.set_value(1)
                YELLOW.set_value(0)
        else:
            person_detected = False
            RED.set_value(0)
            YELLOW.set_value(1)
            
        cv2.imshow('YOLO Object Detection', frame)
        cv2.waitKey(1)

finally:
    cv2.destroyAllWindows()
    piCam.stop()

    RED.set_value(0)
    GREEN.set_value(0)
    YELLOW.set_value(0)
    RED.release()
    YELLOW.release()
    GREEN.release()
