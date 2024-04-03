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
    while True:
        frame = piCam.capture_array()
        results = model(frame)

        class_counts = {}

        for *xyxy, conf, cls in results.xyxy[0]:
            class_id = int(cls)
            class_name = results.names[class_id]

            class_counts[class_name] = class_counts.get(class_name, 0) + 1

        for class_name, count in class_counts.items():
            print(f'{class_name}: {count}')

        RED.set_value(1 if class_counts.get("person", 0) > 0 else 0)
        YELLOW.set_value(1 if class_counts.get("car", 0) > 0 else 0)
        GREEN.set_value(1 if class_counts.get("dog", 0) > 0 else 0)

finally:
    cv2.destroyAllWindows()
    piCam.stop()
    RED.set_value(0)
    GREEN.set_value(0)
    YELLOW.set_value(0)
    RED.release()
    YELLOW.release()
    GREEN.release()
