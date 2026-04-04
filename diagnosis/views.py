from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import os
import tempfile
import torch

from .ml_model.classifier import model, device, load_image, idx_to_class
from .ml_model.gradcam import generate_gradcam
from .ml_model.lime_explain import generate_lime
from .ml_model.shap_explain import generate_shap
from .models import DiagnosisResult
from accounts.models import User


# ─────────────────────────────────────────────────────────
#  Doctor: upload scan + run inference
# ─────────────────────────────────────────────────────────
class PredictView(APIView):
    parser_classes   = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        # ── Validate image ────────────────────────────────
        if 'image' not in request.FILES:
            return Response(
                {"error": "No image sent. Use key 'image'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ── Read patient fields ───────────────────────────
        patient_name   = request.data.get('patient_name',   '')
        patient_age    = request.data.get('patient_age',    None)
        patient_gender = request.data.get('patient_gender', '')
        patient_id     = request.data.get('patient_id',     None)

        # ── Resolve patient user (optional) ──────────────
        patient_user = None
        if patient_id:
            try:
                patient_user = User.objects.get(id=patient_id)
            except User.DoesNotExist:
                pass  # link is optional; we still save the name/age/gender

        # ── Save image to temp folder ─────────────────────
        image_file = request.FILES['image']
        temp_dir   = tempfile.gettempdir()
        temp_path  = os.path.join(temp_dir, image_file.name)

        with open(temp_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        try:
            # ── Run prediction ────────────────────────────
            img        = load_image(temp_path)
            img_tensor = torch.tensor(img).unsqueeze(0).to(device)

            model.enable_gradcam = False
            with torch.no_grad():
                logits, _ = model(img_tensor)
                probs      = torch.softmax(logits, dim=1)
                idx        = probs.argmax(dim=1).item()
                confidence = probs.max(dim=1).values.item()

            prediction = {
                "predicted_class": idx_to_class[idx],
                "confidence":      round(confidence * 100, 2),
                "all_probabilities": {
                    idx_to_class[i]: round(probs[0][i].item() * 100, 2)
                    for i in range(4)
                }
            }

            # ── Generate XAI explanations ─────────────────
            print("Generating GradCAM...")
            gradcam_img = generate_gradcam(temp_path)

            print("Generating LIME...")
            lime_img = generate_lime(temp_path)

            print("Generating SHAP...")
            shap_img = generate_shap(temp_path)

            # ── Persist to database ───────────────────────
            result = DiagnosisResult.objects.create(
                doctor          = request.user,
                patient         = patient_user,
                patient_name    = patient_name,
                patient_age     = patient_age,
                patient_gender  = patient_gender,
                mri_image       = image_file,
                predicted_class = prediction['predicted_class'],
                confidence      = prediction['confidence'],
                all_probabilities = prediction['all_probabilities'],
                gradcam_image   = gradcam_img,
                shap_image      = shap_img,
                lime_image      = lime_img,
            )

            # ── Clean up temp file ────────────────────────
            if os.path.exists(temp_path):
                os.remove(temp_path)

            # ── Return response ───────────────────────────
            return Response({
                "success": True,
                "scan_id": result.id,
                "patient": {
                    "name":   patient_name,
                    "age":    patient_age,
                    "gender": patient_gender,
                },
                "prediction":   prediction,
                "explanations": {
                    "gradcam": gradcam_img,
                    "lime":    lime_img,
                    "shap":    shap_img,
                }
            })

        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ─────────────────────────────────────────────────────────
#  Doctor: list all scans they have uploaded
# ─────────────────────────────────────────────────────────
class DoctorReportsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        results = DiagnosisResult.objects.filter(
            doctor=request.user
        ).order_by('-created_at')

        data = [_serialize_result(r) for r in results]
        return Response({"reports": data})


# ─────────────────────────────────────────────────────────
#  Patient: list only their own results
# ─────────────────────────────────────────────────────────
class PatientReportsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        results = DiagnosisResult.objects.filter(
            patient=request.user
        ).order_by('-created_at')

        data = [_serialize_result(r) for r in results]
        return Response({"reports": data})


# ─────────────────────────────────────────────────────────
#  Single scan detail (used by both doctor & patient)
# ─────────────────────────────────────────────────────────
class ScanDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, scan_id):
        try:
            # Allow access only to the owning doctor OR the linked patient
            result = DiagnosisResult.objects.get(id=scan_id)
        except DiagnosisResult.DoesNotExist:
            return Response(
                {"error": "Scan not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        is_doctor  = result.doctor  == request.user
        is_patient = result.patient == request.user

        if not (is_doctor or is_patient):
            return Response(
                {"error": "Not authorised."},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(_serialize_result(result))


# ─────────────────────────────────────────────────────────
#  Doctor: list all patient users (for the patient picker)
# ─────────────────────────────────────────────────────────
class PatientListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Adjust the filter to match your User model's role field name
        patients = User.objects.filter(role='patient').values(
            'id', 'first_name', 'last_name', 'email'
        )
        return Response({"patients": list(patients)})


# ─────────────────────────────────────────────────────────
#  Health check (public)
# ─────────────────────────────────────────────────────────
class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "status":  "running",
            "message": "Dementia Detection API is working!"
        })


# ─────────────────────────────────────────────────────────
#  Shared serialiser helper
# ─────────────────────────────────────────────────────────
def _serialize_result(r):
    return {
        "scan_id":    r.id,
        "created_at": r.created_at.strftime('%b %d, %Y'),
        "doctor_name": (
            r.doctor.get_full_name() if r.doctor else "—"
        ),
        "patient": {
            "name":   r.patient_name,
            "age":    r.patient_age,
            "gender": r.patient_gender,
        },
        "prediction": {
            "predicted_class":   r.predicted_class,
            "confidence":        r.confidence,
            "all_probabilities": r.all_probabilities,
        },
        "explanations": {
            "gradcam": r.gradcam_image,
            "shap":    r.shap_image,
            "lime":    r.lime_image,
        }
    }