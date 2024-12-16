import cv2
import os
import argparse
from tqdm import tqdm

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="Prepare Images",
        description="A script to cut images <width> by <height> pixels from <input> prepare_video from "
                    "<start-second> to <end-second> with step <frame-distance> and save it"
                    "to <output> directory"
    )
    parser.add_argument('-s', '--start-second', required=True, type=int)
    parser.add_argument('-e', '--end-second', required=True, type=int)
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('-d', '--frame-distance', required=True, type=int)
    parser.add_argument('-w', '--width', required=False, type=int)
    parser.add_argument('-l', '--height', required=False, type=int)

    args = parser.parse_args()

    VIDEO_PATH = args.input
    START_SECOND = args.start_second
    END_SECOND = args.end_second
    FRAME_DISTANCE = args.frame_distance
    OUT_DIR = args.output

    if FRAME_DISTANCE <= 0:
        print("Frame distance should be positive")
        exit(-1)

    capture = cv2.VideoCapture(VIDEO_PATH)

    if not capture.isOpened():
        print("Error opening prepare_video")
        exit(-1)

    OUT_WIDTH = args.width
    OUT_HEIGHT = args.height

    real_frame_width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    real_frame_height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

    needs_resize = (OUT_WIDTH is not None) or (OUT_HEIGHT is not None)

    if OUT_WIDTH is None:
        OUT_WIDTH = real_frame_width

    if OUT_HEIGHT is None:
        OUT_HEIGHT = real_frame_height

    if OUT_WIDTH <= 0:
        print("Image width should be positive")
        exit(-1)

    if OUT_HEIGHT <= 0:
        print("Image height should be positive")
        exit(-1)

    total_frames = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = capture.get(cv2.CAP_PROP_FPS)

    if START_SECOND <= 0:
        print(f'Start second should be positive integer')
        exit(-1)

    if END_SECOND < START_SECOND:
        print(f'End second should be not less than start second')
        exit(-1)

    START_FRAME = (START_SECOND - 1) * fps
    END_FRAME = (END_SECOND - 1) * fps

    START_FRAME = min(START_FRAME, total_frames)
    END_FRAME = min(END_FRAME, total_frames)

    capture.set(cv2.CAP_PROP_POS_FRAMES, START_FRAME - 1)
    cur_frame = START_FRAME

    img_id = 0

    total_iterations = int((END_FRAME - START_FRAME) // FRAME_DISTANCE) + 1

    for i in tqdm(range(total_iterations)):
        capture.set(cv2.CAP_PROP_POS_FRAMES, cur_frame - 1)

        ret, frame = capture.read()
        if not ret:
            break

        if needs_resize:
            frame = cv2.resize(frame, (OUT_WIDTH, OUT_HEIGHT))

        cv2.imwrite(os.path.join(OUT_DIR, f'{img_id}.png'), frame)
        cur_frame += FRAME_DISTANCE
        img_id += 1

    capture.release()