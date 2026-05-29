from django.db import models


class ImportBatch(models.Model):

    SOURCE_CHOICES = [
        ('sap', 'SAP'),
        ('utility', 'Utility'),
        ('travel', 'Travel'),
    ]

    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]

    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES
    )

    file_name = models.CharField(max_length=255)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    def __str__(self):
        return f"{self.source_type} - {self.file_name}"


class RawRecord(models.Model):

    batch = models.ForeignKey(
        ImportBatch,
        on_delete=models.CASCADE
    )

    raw_data = models.JSONField()

    status = models.CharField(
        max_length=20,
        default='pending'
    )

    error_message = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"RawRecord {self.id}"


class NormalizedActivity(models.Model):

    REVIEW_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    source_type = models.CharField(max_length=20)

    activity_date = models.DateField(
        null=True,
        blank=True
    )

    category = models.CharField(max_length=100)

    quantity = models.FloatField(
        null=True,
        blank=True
    )

    unit = models.CharField(
        max_length=50,
        blank=True
    )

    normalized_quantity = models.FloatField(
        null=True,
        blank=True
    )

    normalized_unit = models.CharField(
        max_length=50,
        blank=True
    )

    emissions = models.FloatField(
        null=True,
        blank=True
    )

    scope = models.CharField(
    max_length=20,
    default="Unknown"
)

    review_status = models.CharField(
        max_length=20,
        choices=REVIEW_CHOICES,
        default='pending'
    )

    raw_record = models.ForeignKey(
        RawRecord,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.source_type} - {self.category}"
    

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    activity = models.ForeignKey(
        "NormalizedActivity",
        on_delete=models.CASCADE,
        related_name="audit_logs"
    )
    analyst_id = models.EmailField()
    analyst_location = models.CharField(max_length=150)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.activity_id} - {self.action} - {self.analyst_id}"