import io

import av
import numpy as np
import cv2

from .request import make_request

class Model:
    def __init__(
            self,
            node_id: str,
            folder_id: str,
            model_id: str,
            img_size: int,
            input_type: str = 'FP32'
    ):
        self.node_id = node_id
        self.folder_id = folder_id
        self.model_id = model_id
        self.img_size = img_size
        self.input_type = input_type

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

        image = image / 127.5 - 1.0

        image = cv2.resize(image, (self.img_size, self.img_size))

        return image

    def postprocess_image(self, image: np.ndarray, initial_shape: tuple) -> np.ndarray:
        image = (image + 1.0) / 2.0

        new_height, new_width = self.get_result_size(initial_shape[0], initial_shape[1])

        image = cv2.resize(image, (new_width, new_height))

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

            frames.append(self.preprocess_image(frame))

        capture.release()

        frames_out: list[np.ndarray] = []

        for i in range(0, len(frames), 24):
            sublist = frames[i:i+24]
            while len(sublist) < 24:
                sublist.append(np.zeros((self.img_size, self.img_size, 3)))

            frames_nd = np.array(sublist)

            print(self.input_type)

            if self.input_type == 'FP16':
                frames_nd = np.float16(frames_nd)

            frames_nd = np.moveaxis(frames_nd, (0, 1, 2, 3), (0, 2, 3, 1))

            print(frames_nd.shape)

            frames_nd = make_request(
                node_id=self.node_id,
                folder_id=self.folder_id,
                model_id=self.model_id,
                model_input=frames_nd
            )

            frames_nd = np.moveaxis(frames_nd, (0, 1, 2, 3), (0, 3, 1, 2))

            for frame in frames_nd:
                frames_out.append(self.postprocess_image(frame, (height, width)))

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