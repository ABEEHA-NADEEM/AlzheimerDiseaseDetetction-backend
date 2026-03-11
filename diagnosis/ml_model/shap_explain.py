import numpy as np
import torch
import shap
import base64
import cv2
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .classifier import model, device, load_image

def shap_predict(images):
    model.enable_gradcam = False
    images_uint8 = [img.astype(np.uint8) for img in images]
    inputs = model.feature_extractor(
        images=images_uint8, return_tensors="pt"
    )
    pixel_values = inputs["pixel_values"].to(device)

    with torch.no_grad():
        out = model.model(pixel_values).pooler_output
        x = model.relu(model.fc1(out))
        x = model.fc2(x)
        logits = model.fc3(x)
        probs = torch.softmax(logits, dim=1)

    return probs.cpu().numpy()

def generate_shap(img_path):
    try:
        img = load_image(img_path)
        img_float = img.astype(np.float32) / 255.0
        img_batch = np.expand_dims(img_float, axis=0)

        masker = shap.maskers.Image(
            "blur(16,16)", img_float.shape
        )
        explainer = shap.Explainer(
            shap_predict,
            masker,
            algorithm="partition"
        )
        shap_values = explainer(
            img_batch,
            max_evals=200,
            batch_size=10
        )

        # Save SHAP plot to buffer
        plt.figure(figsize=(10, 4))
        shap.image_plot(
            shap_values,
            img_batch,
            show=False
        )

        buf = io.BytesIO()
        plt.savefig(buf, format='jpg', bbox_inches='tight')
        plt.close()
        buf.seek(0)

        img_base64 = base64.b64encode(
            buf.read()
        ).decode('utf-8')

        return img_base64

    except Exception as e:
        print(f"SHAP error: {e}")
        return None