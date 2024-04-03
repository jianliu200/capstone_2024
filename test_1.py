import gpiod
import time
import signal
import sys
import cv2
import torch
from picamera2 import Picamera2
from ultralytics import YOLO

LED_PIN1 = 9
LED_PIN2 = 10
LED_PIN3 = 11

chip = gpiod.Chip('gpiochip4')

RED = chip.get_line(LED_PIN1)
YELLOW = chip.get_line(LED_PIN2)
GREEN = chip.get_line(LED_PIN3)


RED.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
YELLOW.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
GREEN.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)




model = YOLO('yolov8n.pt')

x_line = 100

piCam = Picamera2()
config = piCam.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"}, controls={"FrameRate": 30})
piCam.configure(config)
piCam.start()


while True:
	frame = piCam.capture_array()
	results = model(frame, stream=True)
		       
	if cv2.waitKey(1) == ord("q"):
		break
			
	detect_count = 0
 
 	for result in results:
		names = results.names
		detect_count = len(result.boxes)
    
    print(f'Detecting: {detect_count}')
    
cv2.destroyAllWindows()
piCam.stop()


RED.set_value(0)
GREEN.set_value(0)
YELLOW.set_value(0)
RED.release()
YELLOW.release()
GREEN.release()



# RED.set_value(1)
# YELLOW.set_value(1)
# GREEN.set_value(1)
# time.sleep(1)
# RED.set_value(0)
# GREEN.set_value(0)
# YELLOW.set_value(0)

   
