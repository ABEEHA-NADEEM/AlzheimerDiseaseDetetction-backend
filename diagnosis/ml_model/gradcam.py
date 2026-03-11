import numpy as np
import cv2
import torch
import base64
from .classifier import model, device, load_image

def generate_gradcam(img_path):
    try:
        img = load_image(img_path)
        img_tensor = torch.tensor(img).unsqueeze(0).to(device)

        model.enable_gradcam = True
        model.zero_grad()

        logits, features = model(img_tensor)
        class_idx = logits.argmax(dim=1)
        logits[0, class_idx].backward()

        grads = model.gradients
        if grads is None:
            return None

        weights = grads.mean(dim=(2, 3), keepdim=True)
        cam = (weights * features).sum(dim=1).squeeze()
        cam = cam.detach().cpu().numpy()
        cam = np.maximum(cam, 0)
        cam = cv2.resize(cam, (300, 300))
        cam = cam / (cam.max() + 1e-8)

        heatmap = cv2.applyColorMap(
            np.uint8(255 * cam), cv2.COLORMAP_JET
        )
        overlay = (heatmap * 0.4 + img).astype(np.uint8)

        model.enable_gradcam = False

        # Convert to base64 to send via API
        _, buffer = cv2.imencode('.jpg', overlay)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        return img_base64

    except Exception as e:
        print(f"GradCAM error: {e}")
        return None