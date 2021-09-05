import cv2
import time

cap = cv2.VideoCapture(0)

for frame in range(10):
    _, last_frame = cap.read()
last_frame = cv2.flip(last_frame, 1)
last_frame = cv2.cvtColor(last_frame, cv2.COLOR_BGR2GRAY)
last_frame = cv2.GaussianBlur(last_frame, (25, 25), 0)

while True:

    _, unprocessed_frame = cap.read()
    #frame = cv2.resize(frame, (200, 800)
    unprocessed_frame = cv2.flip(unprocessed_frame, 1)
    frame = cv2.cvtColor(unprocessed_frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.GaussianBlur(frame, (25, 25), 0)
    
    foreground = cv2.absdiff(frame, last_frame)
    _, mask = cv2.threshold(foreground, 15, 255, cv2.THRESH_BINARY)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) < 800:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(unprocessed_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("processed", mask)
    cv2.imshow("Webcam", unprocessed_frame)
    

    last_frame = frame

    if cv2.waitKey(1) == ord('q'):
        break

