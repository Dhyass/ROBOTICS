# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 10:17:01 2024

@author: magnn
"""

import picamera
import picamera.array
import cv2
import numpy as np

def calculate_distance_and_coordinates(cnt):
    M = cv2.moments(cnt)
    if M['m00'] != 0:
        Cx = int(M['m10'] / M['m00'])
        Cy = int(M['m01'] / M['m00'])
        distance = 0.0003 * (Cy ** 2) - (0.3178 * Cy) + 103.53
        return Cx, Cy, distance
    else:
        return None, None, None

def main():
    distance = 0
    font = cv2.FONT_HERSHEY_COMPLEX
    kernel = np.ones((3, 3), np.uint8)

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'XVID' for AVI format
    out = cv2.VideoWriter('output_video.mp4', fourcc, 30.0, (640, 480))

    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 30

        with picamera.array.PiRGBArray(camera) as output:
            for frame in camera.capture_continuous(output, format='bgr', use_video_port=True):
                frame = output.array
                frame = cv2.flip(frame, 1)

                frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                # Define the HSV range for yellow color
                lower_yellow = np.array([20, 100, 100])
                upper_yellow = np.array([30, 255, 255])

                # Create a mask to extract yellow objects
                mask = cv2.inRange(frame_hsv, lower_yellow, upper_yellow)
                cv2.imshow('Masked Image', mask)

                # Perform morphological opening to remove noise
                opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                cv2.imshow('Opening', opening)

                # Apply the mask to the original frame
                result = cv2.bitwise_and(frame, frame, mask=opening)
                cv2.imshow('Resulting Image', result)

                # Find contours in the masked image
                contours, hierarchy = cv2.findContours(opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

                # Analyze the largest contour (by area)
                if contours:
                    cnt = max(contours, key=cv2.contourArea)
                    area = cv2.contourArea(cnt)
                    if area > 100:
                        # Calculate centroid coordinates and distance
                        Cx, Cy, distance = calculate_distance_and_coordinates(cnt)
                        if Cx is not None and Cy is not None:
                            # Display location and area information on the frame
                            location_text = 'Location of object: ({}, {})'.format(Cx, Cy)
                            cv2.putText(frame, location_text, (5, 50), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
                            area_text = 'Area of contour: {}'.format(area)
                            cv2.putText(frame, area_text, (5, 80), font, 1, (0, 0, 255), 2, cv2.LINE_AA)

                # Display the distance information on the frame
                distance_text = 'Distance Of Object: {:.2f}'.format(distance)
                cv2.putText(frame, distance_text, (5, 110), font, 1, (0, 0, 255), 2, cv2.LINE_AA)

                # Draw contours on the frame
                cv2.drawContours(frame, contours, -1, (0, 255, 0), 3)

                # Display the original frame with applied processing
                cv2.imshow('Original Image', frame)

                # Write the frame to the video file
                out.write(frame)

                # Clear the stream in preparation for the next frame
                output.truncate(0)

                # Exit the loop if 's' key is pressed
                if cv2.waitKey(1) == ord('s'):
                    break

    # Release the VideoWriter object
    out.release()

    # Close all OpenCV windows
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
