import numpy

from AnimeGAN.telegram.datasphere.request import make_request

class Model:
    def __init__(self, node_id: str, folder_id: str, model_id: str):
        self.node_id = node_id
        self.folder_id = folder_id
        self.model_id = model_id


    def process(self, data: numpy.ndarray) -> numpy.ndarray:
        return make_request(node_id=self.node_id, folder_id=self.folder_id, model_id=self.model_id, model_input=data)