import cv2
from ultralytics import YOLO

model = YOLO('yolov8n.pt')

x_line = 100


cap = cv2.VideoCapture(0)



while True:
    ret, frame = cap.read()
    if not ret:
        break 

    results = model(frame, stream=True)

    # TESTING PURPOSES:
    # Get center line of frame
    x_middle = frame.shape[1] // 2
    cv2.line(frame, (x_middle, 0), (x_middle, frame.shape[0]), (255, 0, 0), 2)

    # TESTING PURPOSES
    left_count = 0
    right_count = 0

    for result in results:
        for box in result.boxes:
            b = box.xyxy[0]
            x1, y1, x2, y2 = b
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            if x1 < x_middle:
                left_count += 1
            else:
                right_count += 1
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    cv2.putText(frame, f'Left: {left_count}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f'Right: {right_count}', (frame.shape[1] - 200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    print(f'Left: {left_count}, Right: {right_count}')

    cv2.imshow('YOLO Object Detection', frame)
    
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
