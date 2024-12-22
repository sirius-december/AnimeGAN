import tritonclient.http as httpclient
from .util.iam import generate_jwt, get_iam_token_jwt, get_iam_token
import numpy as np

triton_client = httpclient.InferenceServerClient(url='node-api.datasphere.yandexcloud.net', ssl=True)

def make_request(node_id: str, folder_id: str, model_id: str, model_input, datatype: str = "FP32"):
    # iam_token = get_iam_token_jwt(generate_jwt())
    iam_token = get_iam_token()

    headers = {
        "Authorization": f"Bearer {iam_token}",
        "x-node-id": f"{node_id}",
        "x-folder-id": f"{folder_id}"
    }

    input_shape = model_input.shape
    payload = httpclient.InferInput("input_variable_0", input_shape, datatype)

    input_batch = np.array(model_input)
    payload.set_data_from_numpy(input_batch, binary_data=False)

    inputs = [payload]
    results = triton_client.infer(model_id, inputs=inputs, headers=headers)

    return results.as_numpy("output_variable_0")


