from rest_framework import serializers
from .models import ImportBatch, RawRecord, NormalizedActivity
from .models import AuditLog


class ImportBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportBatch
        fields = '__all__'


class RawRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawRecord
        fields = '__all__'


class NormalizedActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = NormalizedActivity
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"