import numpy as np
import torch
import base64
import cv2
from PIL import Image
from lime import lime_image
from skimage.segmentation import mark_boundaries
from .classifier import model, device, load_image

def lime_predict(images):
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

def generate_lime(img_path):
    try:
        img = load_image(img_path)

        explainer = lime_image.LimeImageExplainer()
        explanation = explainer.explain_instance(
            img,
            lime_predict,
            top_labels=1,
            hide_color=0,
            num_samples=200   # lower = faster
        )

        temp, mask = explanation.get_image_and_mask(
            explanation.top_labels[0],
            positive_only=True,
            num_features=10,
            hide_rest=False
        )

        lime_img = mark_boundaries(temp, mask)
        lime_img = (lime_img * 255).astype(np.uint8)
        lime_bgr = cv2.cvtColor(lime_img, cv2.COLOR_RGB2BGR)

        # Convert to base64
        _, buffer = cv2.imencode('.jpg', lime_bgr)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        return img_base64

    except Exception as e:
        print(f"LIME error: {e}")
        return None