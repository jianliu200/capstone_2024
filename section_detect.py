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
    sidewalk_person_detected = False
    street_person_detected = False

    sidewalk_start_time = None
    street_start_time = None

    while True:
        frame = piCam.capture_array()
        results = model(frame, stream=True)

        sidewalk_class_counts = {}
        street_class_counts = {}

        # Get the dimensions of the image
        height, width, channels = frame.shape

        # Calculate the center of the image
        center_x = width // 2
        center_y = height // 2


        # top sidewalk line
        top_sidewalk_slope = ( (center_y - (height // 4) - (height // 8)) - (center_y - (height // 4)) ) / width
        top_sidewalk_intercept = center_y - (height // 4)

        # bottom sidewalk line slope
        bottom_sidewalk_slope = ( (center_y - (height // 4) + (height // 8)) - (height) ) / width
        bottom_sidewalk_intercept = height

        # Plot the lines using the calculated slopes and y-intercepts
        cv2.line(frame, (0, int(top_sidewalk_intercept)), (width, int(top_sidewalk_slope * width + top_sidewalk_intercept)), (0, 0, 255), 2)
        cv2.line(frame, (0, int(bottom_sidewalk_intercept)), (width, int(bottom_sidewalk_slope * width + bottom_sidewalk_intercept)), (0, 0, 255), 2)

        for result in results:
            for box in result.boxes:
                class_name = result.names[int(box.cls)]

                b = box.xyxy[0]
                x1, y1, x2, y2 = b
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)


                # Check street section first
                #if x1 > center_y:
                if y2 > (top_sidewalk_slope * x2 + top_sidewalk_intercept) and y2 < (bottom_sidewalk_slope * x2 + bottom_sidewalk_intercept):
                    street_class_counts[class_name] = street_class_counts.get(class_name, 0) + 1
                else:
                    sidewalk_class_counts[class_name] = sidewalk_class_counts.get(class_name, 0) + 1

                #cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)


        # PEOPLE ON STREET: RED
        if "person" in street_class_counts and street_class_counts["person"] > 0:
            if not street_person_detected:
                street_person_detected = True
                sidewalk_person_detected = False
                RED.set_value(1)
                YELLOW.set_value(0)
                GREEN.set_value(0)

        # PEOPLE WAITING ON SIDEWALK: YELLOW
        elif "person" in sidewalk_class_counts and sidewalk_class_counts["person"] > 0:
            if not sidewalk_person_detected:
                sidewalk_start_time = time.time()
                sidewalk_person_detected = True
                street_person_detected = False
            elif time.time() - sidewalk_start_time >= 1:  # Wait for 2 seconds before switching lights
                RED.set_value(0)
                YELLOW.set_value(1)
                GREEN.set_value(0)

        # NOBODY IN SIGHT: GREEN
        else:
            sidewalk_person_detected = False
            street_person_detected = False
            RED.set_value(0)
            YELLOW.set_value(0)
            GREEN.set_value(1)

        print(f'Detecting on the SIDEWALK: {sidewalk_class_counts}')
        print(f'Detecting on the STREET: {street_class_counts}')

        #cv2.imshow('YOLO Object Detection', frame)

        #if cv2.waitKey(1) == ord('q'):
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

