from django.db import models
from accounts.models import User


class DiagnosisResult(models.Model):
    # Who uploaded
    doctor      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Patient info
    patient_name = models.CharField(max_length=100, blank=True)
    patient_age  = models.IntegerField(null=True, blank=True)
    patient_gender = models.CharField(max_length=20, blank=True)

    # MRI image
    mri_image    = models.ImageField(upload_to='mri_uploads/')

    # Prediction results
    predicted_class = models.CharField(max_length=100)
    confidence      = models.FloatField()
    all_probabilities = models.JSONField(default=dict)

    # Explainability images (stored as base64)
    gradcam_image = models.TextField(blank=True)
    shap_image    = models.TextField(blank=True)
    lime_image    = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} — {self.predicted_class} ({self.confidence}%)"