import cv2
import os
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="Prepare Images",
        description="A script to cut images <width> by <height> pixels from <input> video from "
                    "<start-frame> to <end-frame> with step <frame-distance> and save it"
                    "to <output> directory"
    )
    parser.add_argument('-s', '--start-frame', required=True, type=int)
    parser.add_argument('-e', '--end-frame', required=True, type=int)
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('-d', '--frame-distance', required=True, type=int)
    parser.add_argument('-w', '--width', required=True, type=int)
    parser.add_argument('-l', '--height', required=True, type=int)

    args = parser.parse_args()

    VIDEO_PATH = args.input
    START_FRAME = args.start_frame
    END_FRAME = args.end_frame
    OUT_WIDTH = args.width
    OUT_HEIGHT = args.height
    FRAME_DISTANCE = args.frame_distance
    OUT_DIR = args.output

    if OUT_WIDTH <= 0:
        print("Image width should be positive")
        exit(-1)

    if OUT_HEIGHT <= 0:
        print("Image height should be positive")
        exit(-1)

    if FRAME_DISTANCE < 0:
        print("Frame distance should be positive")
        exit(-1)

    capture = cv2.VideoCapture(VIDEO_PATH)

    if not capture.isOpened():
        print("Error opening video")
        exit(-1)

    total_frames = capture.get(cv2.CAP_PROP_FRAME_COUNT)

    if START_FRAME <= 0 or START_FRAME > total_frames:
        print(f'Start frame should be in range [1, {total_frames}], because video have {total_frames} frames')
        exit(-1)

    if END_FRAME < START_FRAME or END_FRAME > total_frames:
        print(f'End frame should be in range [{START_FRAME}, {total_frames}], because video have {total_frames} '
              f'frames and first frame is {START_FRAME}')
        exit(-1)

    capture.set(cv2.CAP_PROP_POS_FRAMES, START_FRAME - 1)
    cur_frame = START_FRAME

    img_id = 0

    while cur_frame <= END_FRAME:
        ret, frame = capture.read()
        if not ret:
            break

        if (cur_frame - START_FRAME) % FRAME_DISTANCE != 0:
            cur_frame += 1
            continue

        cur_frame += 1

        frame = cv2.resize(frame, (OUT_WIDTH, OUT_HEIGHT))
        cv2.imwrite(os.path.join(OUT_DIR, f'{img_id}.png'), frame)
        img_id += 1

    capture.release()