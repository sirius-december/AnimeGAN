import cv2
from PIL import Image 

def crop_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    fps = 24
    width = 512
    height = 512
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    out = cv2.VideoWriter(output_path, fourcc, fps,(512, 512))

    frame_count = 0
    while cap.isOpened() and frame_count < fps * 10:
        ret, frame = cap.read()
        if not ret:
            break

        frame = frame.thumbnail((width, height))
        out.write(frame)
        frame_count += 1

    cap.release()
    out.release()

crop_video('input_video.mp4', 'output_video.mp4')