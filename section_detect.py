def initialize_led_pins():
  """
  Initializes the LED pins as output pins.
  """
  LED_PIN1, LED_PIN2, LED_PIN3 = 9, 10, 11

  chip = gpiod.Chip('gpiochip4')
  RED = chip.get_line(LED_PIN1)
  YELLOW = chip.get_line(LED_PIN2)
  GREEN = chip.get_line(LED_PIN3)

  RED.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
  YELLOW.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
  GREEN.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)

  return RED, YELLOW, GREEN


def initialize_model():
  """
  Initializes the YOLO model for object detection.
  """
  model = YOLO('yolov8n.pt')
  return model


def initialize_camera():
  """
  Initializes the PiCamera for capturing images.
  """
  piCam = Picamera2()
  config = piCam.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"}, controls={"FrameRate": 30})
  piCam.configure(config)
  piCam.start()

  return piCam


def detect_objects(frame, model):
  """
  Performs object detection on the given frame using the YOLO model.
  Returns the detection results.
  """
  results = model(frame, stream=True)
  return results


def draw_sidewalk_lines(frame, center_x, center_y, height, width):
  """
  Draws the sidewalk lines on the given frame.
  """
  top_sidewalk_slope = ((center_y - (height // 4) - (height // 8)) - (center_y - (height // 4))) / width
  top_sidewalk_intercept = center_y - (height // 4)

  bottom_sidewalk_slope = ((center_y - (height // 4) + (height // 8)) - (height)) / width
  bottom_sidewalk_intercept = height

  cv2.line(frame, (0, int(top_sidewalk_intercept)), (width, int(top_sidewalk_slope * width + top_sidewalk_intercept)), (0, 0, 255), 2)
  cv2.line(frame, (0, int(bottom_sidewalk_intercept)), (width, int(bottom_sidewalk_slope * width + bottom_sidewalk_intercept)), (0, 0, 255), 2)


def process_results(results, frame, sidewalk_class_counts, street_class_counts, center_y, top_sidewalk_slope, top_sidewalk_intercept, bottom_sidewalk_slope, bottom_sidewalk_intercept):
  """
  Processes the object detection results and updates the class counts.
  """
  for result in results:
    for box in result.boxes:
      class_name = result.names[int(box.cls)]

      b = box.xyxy[0]
      x1, y1, x2, y2 = b
      x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

      if y2 > (top_sidewalk_slope * x2 + top_sidewalk_intercept) and y2 < (bottom_sidewalk_slope * x2 + bottom_sidewalk_intercept):
        street_class_counts[class_name] = street_class_counts.get(class_name, 0) + 1
      else:
        sidewalk_class_counts[class_name] = sidewalk_class_counts.get(class_name, 0) + 1


def update_led_lights(sidewalk_class_counts, street_class_counts, sidewalk_person_detected, street_person_detected, RED, YELLOW, GREEN):
  """
  Updates the LED lights based on the detected objects.
  """
  if "person" in street_class_counts and street_class_counts["person"] > 0:
    if not street_person_detected:
      street_person_detected = True
      sidewalk_person_detected = False
      RED.set_value(1)
      YELLOW.set_value(0)
      GREEN.set_value(0)
  elif "person" in sidewalk_class_counts and sidewalk_class_counts["person"] > 0:
    if not sidewalk_person_detected:
      sidewalk_start_time = time.time()
      sidewalk_person_detected = True
      street_person_detected = False
    elif time.time() - sidewalk_start_time >= 1:
      RED.set_value(0)
      YELLOW.set_value(1)
      GREEN.set_value(0)
  else:
    sidewalk_person_detected = False
    street_person_detected = False
    RED.set_value(0)
    YELLOW.set_value(0)
    GREEN.set_value(1)

  return sidewalk_person_detected, street_person_detected


def main():
  """
  Main function to run the object detection and LED control.
  """
  RED, YELLOW, GREEN = initialize_led_pins()
  model = initialize_model()
  piCam = initialize_camera()

  try:
    sidewalk_person_detected = False
    street_person_detected = False

    sidewalk_start_time = None

    while True:
      frame = piCam.capture_array()
      results = detect_objects(frame, model)

      sidewalk_class_counts = {}
      street_class_counts = {}

      height, width, channels = frame.shape
      center_x = width // 2
      center_y = height // 2

      draw_sidewalk_lines(frame, center_x, center_y, height, width)

      process_results(results, frame, sidewalk_class_counts, street_class_counts, center_y, top_sidewalk_slope, top_sidewalk_intercept, bottom_sidewalk_slope, bottom_sidewalk_intercept)

      sidewalk_person_detected, street_person_detected = update_led_lights(sidewalk_class_counts, street_class_counts, sidewalk_person_detected, street_person_detected, RED, YELLOW, GREEN)

      print(f'Detecting on the SIDEWALK: {sidewalk_class_counts}')
      print(f'Detecting on the STREET: {street_class_counts}')

  finally:
    cv2.destroyAllWindows()
    piCam.stop()

    RED.set_value(0)
    GREEN.set_value(0)
    YELLOW.set_value(0)
    RED.release()
    YELLOW.release()
    GREEN.release()

