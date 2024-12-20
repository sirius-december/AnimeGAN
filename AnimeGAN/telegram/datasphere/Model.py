import io

import av
import numpy as np
import cv2

from AnimeGAN.telegram.datasphere.request import make_request

class Model:
    def __init__(
            self,
            node_id: str,
            folder_id: str,
            model_id: str,
            img_size: int
    ):
        self.node_id = node_id
        self.folder_id = folder_id
        self.model_id = model_id
        self.img_size = img_size

    def process_image(self, image: np.ndarray) -> np.ndarray:
        shape = image.shape
        image = self.preprocess_image(image)

        image = np.moveaxis(image, (0, 1, 2), (1, 2, 0))

        result = make_request(
            node_id=self.node_id,
            folder_id=self.folder_id,
            model_id=self.model_id,
            model_input=np.array([image])
        )[0]

        result = np.moveaxis(result, (0, 1, 2), (2, 0, 1))


        result = self.postprocess_image(result, shape)

        return result

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        image = image.astype(np.float32)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        w = image.shape[1]
        h = image.shape[0]

        if w > h:
            left = w - h
            image = cv2.copyMakeBorder(image, left=0, right=0, top=0, bottom=left, borderType=cv2.BORDER_CONSTANT)
        elif h > w:
            left = h - w
            image = cv2.copyMakeBorder(image, left=0, right=left, top=0, bottom=0, borderType=cv2.BORDER_CONSTANT)

        image = image / 127.5 - 1.0

        image = cv2.resize(image, (self.img_size, self.img_size))

        return image

    def postprocess_image(self, image: np.ndarray, initial_shape: tuple) -> np.ndarray:
        image = (image + 1.0) / 2.0

        new_height, new_width = self.get_result_size(initial_shape[0], initial_shape[1])

        image = image[0 : new_height, 0 : new_width]

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        image = np.uint8(image * 256)

        return image

    def process_video(self, capture: cv2.VideoCapture) -> io.BytesIO:
        frames: list[np.ndarray] = []
        fps = capture.get(cv2.CAP_PROP_FPS)
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))

        new_height, new_width = self.get_result_size(height, width)

        while True:
            ret, frame = capture.read()

            if not ret:
                break

            frames.append(self.process_image(frame))

        capture.release()

        output_file = io.BytesIO()
        output = av.open(output_file, 'w', format='mp4')
        stream = output.add_stream('h264', int(fps))
        stream.height = new_height
        stream.width = new_width

        for frame in frames:
            av_frame = av.VideoFrame.from_ndarray(frame, format='bgr24')
            packet = stream.encode(av_frame)
            output.mux(packet)

        packet = stream.encode(None)
        output.mux(packet)

        output.close()

        return output_file

    def get_result_size(self, height: int, width: int) -> (int, int):
        ratio = height / width

        if ratio > 1:
            return self.img_size, int(self.img_size / ratio)

        elif ratio < 1:
            return int(self.img_size * ratio), self.img_size

        else:
            return self.img_size, self.img_size