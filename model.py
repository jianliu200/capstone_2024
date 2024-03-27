import cv2
import torch
from picamera2 import Picamera2
from ultralytics import YOLO


model = YOLO('yolov8n.pt')


piCam = Picamera2()
config = piCam.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"}, controls={"FrameRate": 30})
piCam.configure(config)
piCam.start()

while True:
	frame = piCam.capture_array()
	results = model(frame, stream=True)
		
	# cv2.imshow("piCam",frame)	
	if cv2.waitKey(1) == ord("q"):
		break
			
	for result in results:
		boxes = result.boxes
		probs = result.probs
			
cv2.destroyAllWindows()
piCam.stop()
