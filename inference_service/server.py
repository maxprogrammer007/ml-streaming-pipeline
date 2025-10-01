import grpc
import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights
from PIL import Image
from concurrent import futures
import requests
import json
import os

# Import the generated gRPC files
import protos.inference_pb2 as inference_pb2
import protos.inference_pb2_grpc as inference_pb2_grpc

# --- 1. Model & Label Loading ---

# URL for ImageNet class labels
IMAGENET_LABELS_URL = "https://storage.googleapis.com/download.tensorflow.org/data/imagenet_class_index.json"
LABELS_PATH = "imagenet_labels.json"

def download_labels():
    """Downloads and caches ImageNet labels if they don't exist."""
    if not os.path.exists(LABELS_PATH):
        print("Downloading ImageNet labels...")
        response = requests.get(IMAGENET_LABELS_URL)
        response.raise_for_status()
        with open(LABELS_PATH, 'w') as f:
            f.write(response.text)
    # Load labels into a more usable format {class_id: "class_name"}
    with open(LABELS_PATH) as f:
        labels_json = json.load(f)
    return {int(k): v[1] for k, v in labels_json.items()}

# Load the pretrained ResNet18 model
print("Loading ResNet18 model...")
model = resnet18(weights=ResNet18_Weights.DEFAULT)
model.eval() # IMPORTANT: Set the model to evaluation mode
labels = download_labels()
print("Model and labels loaded successfully.")

# Define the image preprocessing pipeline
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# --- 2. gRPC Service Implementation ---

class InferenceServiceImpl(inference_pb2_grpc.InferenceServiceServicer):
    def Predict(self, request, context):
        """
        This method is called by the client. It receives an image,
        runs inference, and returns the prediction.
        """
        try:
            # Step A: Decode the incoming image bytes
            np_arr = np.frombuffer(request.image_data, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            # Step B: Convert image format from OpenCV (BGR) to what PyTorch expects (RGB)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)

            # Step C: Preprocess the image using the defined pipeline
            input_tensor = preprocess(img_pil)
            input_batch = input_tensor.unsqueeze(0)  # Create a batch of 1

            # Step D: Run inference
            with torch.no_grad(): # No need to calculate gradients
                output = model(input_batch)
            
            # Step E: Get the top prediction
            _, pred_idx = torch.max(output, 1)
            prediction_label = labels[pred_idx.item()]
            
            print(f"Prediction successful: {prediction_label}")
            return inference_pb2.PredictionResponse(prediction=prediction_label)

        except Exception as e:
            print(f"An error occurred during inference: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {e}")
            return inference_pb2.PredictionResponse()

# --- 3. Start the Server ---

def serve():
    """Starts the gRPC server on port 50051."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inference_pb2_grpc.add_InferenceServiceServicer_to_server(InferenceServiceImpl(), server)
    
    port = "50051"
    server.add_insecure_port(f"[::]:{port}")
    print(f"🚀 Server starting on port {port}...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()