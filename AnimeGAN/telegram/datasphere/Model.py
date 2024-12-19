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

    def process(self, image: np.ndarray) -> np.ndarray:
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

        ratio = initial_shape[0] / initial_shape[1]

        if ratio > 1:
            new_width = int(self.img_size / ratio)
            image = image[0 : self.img_size, 0 : new_width]
        elif ratio < 1:
            new_height = int(self.img_size * ratio)
            image = image[0 : new_height, 0 : self.img_size]

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        return image