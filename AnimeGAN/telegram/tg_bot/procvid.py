import cv2
from PIL import Image
import matplotlib.pyplot as plt
import io
import os

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

def videocheck(vid):
    t = vid.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = vid.get(cv2.CAP_PROP_FPS)
    vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
    f,r=vid.read()
    if(t/fps>=11.0) or (os.path.getsize(vid)>16*1024**2) or (max(len(r),len(r[0]))<=1024):
        return False
    return True


def imagecheck(img):
    image = Image.open(io.BytesIO(img))
    if(max(image.size())<=1024 and os.path.getsize(img) <= 11*1024*1024):
        return True
    return False