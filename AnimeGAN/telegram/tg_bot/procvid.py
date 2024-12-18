import cv2
import matplotlib.pyplot as mplt

import cv2

def crop_video(input_file, output_file):
    cap = cv2.VideoCapture(input_file)
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, fps, (512, 512))
    
    frame_count = 0
    max_frames = int(fps * 10)

    while cap.isOpened() and frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        frame_resized = cv2.resize(frame, (512, 512))
        
        out.write(frame_resized)
        frame_count += 1

    cap.release()
    out.release()

