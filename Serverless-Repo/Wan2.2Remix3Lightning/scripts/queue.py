import base64
import requests

def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

payload = {
    "input": {
        "workflow": json.load(open("api-workflow.json")),
        "input_image": image_to_base64("input_images/your_input.png"),
        "prompt": "your prompt here"
    }
}
