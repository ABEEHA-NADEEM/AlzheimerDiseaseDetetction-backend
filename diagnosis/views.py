from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
import os
import tempfile
import torch

from .ml_model.classifier import model, device, load_image, idx_to_class
from .ml_model.gradcam import generate_gradcam
from .ml_model.lime_explain import generate_lime
from .ml_model.shap_explain import generate_shap

class PredictView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):

        # Check image sent
        if 'image' not in request.FILES:
            return Response(
                {"error": "No image sent. Use key 'image'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save image to Windows temp folder
        image_file = request.FILES['image']
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, image_file.name)

        with open(temp_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        try:
            # Get prediction
            img = load_image(temp_path)
            img_tensor = torch.tensor(img).unsqueeze(0).to(device)

            model.enable_gradcam = False
            with torch.no_grad():
                logits, _ = model(img_tensor)
                probs = torch.softmax(logits, dim=1)
                idx = probs.argmax(dim=1).item()
                confidence = probs.max(dim=1).values.item()

            prediction = {
                "predicted_class": idx_to_class[idx],
                "confidence": round(confidence * 100, 2),
                "all_probabilities": {
                    idx_to_class[i]: round(
                        probs[0][i].item() * 100, 2
                    )
                    for i in range(4)
                }
            }

            # Generate explanations
            print("Generating GradCAM...")
            gradcam_img = generate_gradcam(temp_path)

            print("Generating LIME...")
            lime_img = generate_lime(temp_path)

            print("Generating SHAP...")
            shap_img = generate_shap(temp_path)

            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

            return Response({
                "success": True,
                "prediction": prediction,
                "explanations": {
                    "gradcam": gradcam_img,
                    "lime":    lime_img,
                    "shap":    shap_img
                }
            })

        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "status": "running",
            "message": "Dementia Detection API is working!"
        })




### Server Will Auto Reload

# Django watches for file changes so it will restart automatically. You will see:
# ```
# Watching for file changes with StatReloader
# ✅ Model loaded on cpu