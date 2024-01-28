# -*- coding: utf-8 -*-
"""
Created on Sat Jan 27 15:22:49 2024

@author: magnn
"""

import cv2
import numpy as np

def nothing(x):
    pass

distance = 0
cap = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_COMPLEX
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
Kernal = np.ones((3, 3), np.uint8)

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, +1)
    if not ret:
        break

    if cv2.waitKey(1) == ord('s'):
        break

    frame2 = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lb = np.array([153, 119, 212])
    ub = np.array([255, 255, 255])

    mask = cv2.inRange(frame2, lb, ub)
    cv2.imshow('Masked Image', mask)

    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, Kernal)
    cv2.imshow('Opening', opening)

    res = cv2.bitwise_and(frame, frame, mask=opening)

    contours, hierarchy = cv2.findContours(opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    if len(contours) != 0:
        cnt = contours[0]
        area = cv2.contourArea(cnt)
        if area > 100:
            M = cv2.moments(cnt)
            Cx = int(M['m10'] / M['m00'])
            Cy = int(M['m01'] / M['m00'])
            distance = 0.0003 * (Cy ** 2) - (0.3178 * Cy) + 103.53
            S = 'Location of object:' + '(' + str(Cx) + ',' + str(Cy) + ')'
            cv2.putText(frame, S, (5, 50), font, 2, (0, 0, 255), 2, cv2.LINE_AA)
            S = 'Area of contour: ' + str(area)
            cv2.putText(frame, S, (5, 100), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

    S = 'Distance Of Object: ' + str(distance)
    cv2.putText(frame, S, (5, 150), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.drawContours(frame, cnt, -1, (0, 255, 0), 3)

    cv2.imshow('Original Image', frame)

cap.release()
cv2.destroyAllWindows()
