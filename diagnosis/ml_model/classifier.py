import torch
import torch.nn as nn
from transformers import AutoImageProcessor, EfficientNetModel
from PIL import Image
import numpy as np
import os

# ─── Model Definition ─────────────────────────────────────
class Classifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.feature_extractor = AutoImageProcessor.from_pretrained(
            "google/efficientnet-b3", do_rescale=False
        )
        self.model = EfficientNetModel.from_pretrained(
            "google/efficientnet-b3"
        )
        self.fc1 = nn.Linear(1536, 512)
        self.fc2 = nn.Linear(512, 128)
        self.fc3 = nn.Linear(128, 4)
        self.relu = nn.ReLU()

        self.gradients = None
        self.enable_gradcam = False

    def save_gradient(self, grad):
        self.gradients = grad

    def forward(self, x):
        imgs = self.feature_extractor(
            images=x, return_tensors="pt"
        )
        imgs = {
            k: v.to(next(self.parameters()).device)
            for k, v in imgs.items()
        }
        outputs = self.model(
            imgs["pixel_values"],
            output_hidden_states=True
        )
        features = outputs.hidden_states[-1]

        if self.enable_gradcam and features.requires_grad:
            features.register_hook(self.save_gradient)

        pooled = outputs.pooler_output
        x = self.relu(self.fc1(pooled))
        x = self.fc2(x)
        x = self.fc3(x)
        return x, features

# ─── Labels ───────────────────────────────────────────────
idx_to_class = {
    0: "Mild Dementia",
    1: "Moderate Dementia",
    2: "Non Demented",
    3: "Very Mild Dementia"
}

# ─── Load Model Once ──────────────────────────────────────
device = "cuda" if torch.cuda.is_available() else "cpu"

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    'model_final.pth'
)

model = Classifier().to(device)
model.load_state_dict(
    torch.load(MODEL_PATH, map_location=device)
)
model.eval()
print(f"✅ Model loaded on {device}")

# ─── Image Loader ─────────────────────────────────────────
def load_image(img_path):
    img = Image.open(img_path).convert("RGB")
    img = img.resize((300, 300))
    return np.array(img)

def predict(img_path):
    img = load_image(img_path)
    with torch.no_grad():
        logits, _ = model(img)
        probs = torch.softmax(logits, dim=1)
        idx = probs.argmax(dim=1).item()
        confidence = probs.max(dim=1).values.item()
    return {
        "predicted_class": idx_to_class[idx],
        "confidence": round(confidence * 100, 2),
        "all_probabilities": {
            idx_to_class[i]: round(probs[0][i].item() * 100, 2)
            for i in range(4)
        }
    }