import onnxruntime as ort
import numpy as np
import cv2
from PIL import Image
import io

session = ort.InferenceSession("tomatoNet.onnx")
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

with open("labels_tomato.txt", "r") as f:
    labels = [line.strip() for line in f.readlines()]

def preprocess_image(file_bytes):
    image = Image.open(io.BytesIO(file_bytes)).convert('RGB')
    
    img = np.array(image)
    img = cv2.resize(img, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = img.astype(np.float32)
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, axis=0)
    return img

def predict_image(file_bytes):
    img = preprocess_image(file_bytes)
    output = session.run([output_name], {input_name: img})[0]
    
    predicted_index = int(np.argmax(output))
    label = labels[predicted_index]
    
    confidence = float(output[0][predicted_index])
    
    probabilities = [float(prob) for prob in output[0]]
    
    return {
        "index": predicted_index,
        "label": label,
        "confidence": confidence,
        "probabilities": probabilities
    }

