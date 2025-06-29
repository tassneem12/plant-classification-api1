import os
import torch
import timm
from flask import Flask, request, jsonify
from torchvision import transforms
from PIL import Image
import gdown 


# Flask setup
app = Flask(__name__)

# Model path and Google Drive file ID
model_path = "plant_best_model(1).pth"
google_drive_id = "1orewvjx91kRCpwH_0Zlhc4HbNz3--ybt"


if not os.path.exists(model_path):
    print("Downloading model from Google Drive...")
    url = f"https://drive.google.com/uc?id={google_drive_id}"
    gdown.download(url, model_path, quiet=False)

# Load model function
def load_model(model_path, num_classes):
    model = timm.create_model("efficientnet_b3", pretrained=False, num_classes=num_classes)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model

# Load the trained model
num_classes = 30
model = load_model(model_path, num_classes)

# Class names
class_names = [
    "aloevera", "banana", "bilimbi", "cantaloupe", "cassava", "coconut",
    "corn", "cucumber", "curcuma", "eggplant", "galangal", "ginger",
    "guava", "kale", "longbeans", "mango", "melon", "orange", "paddy",
    "papaya", "peperchili", "pineapple", "pomelo", "shallot", "soybeans",
    "spinach", "sweetpotatoes", "tobacco", "waterapple", "watermelon"
]

# Transformations
transform = transforms.Compose([
    transforms.Resize((240, 240)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                        [0.229, 0.224, 0.225])
])

# Prediction function
def predict_image(file):
    image = Image.open(file).convert("RGB")
    image = transform(image).unsqueeze(0)
    with torch.no_grad():
        output = model(image)
        _, predicted = torch.max(output, 1)
    return class_names[predicted.item()]

# API endpoint
@app.route('/', methods=['POST'])
def predict():
    if 'imagefile' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    file = request.files['imagefile']
    try:
        prediction = predict_image(file)
        return jsonify({"result": prediction})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app locally
if __name__ == '__main__':
    app.run(port=3000, debug=True)