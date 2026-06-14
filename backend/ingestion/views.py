
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import (
    ImportBatch,
    RawRecord,
    NormalizedActivity,
    AuditLog,
)

from .serializers import (
    ImportBatchSerializer,
    RawRecordSerializer,
    NormalizedActivitySerializer,
    AuditLogSerializer,
)


@api_view(['GET'])
def batches_list(request):
    batches = ImportBatch.objects.all().order_by('-uploaded_at')
    serializer = ImportBatchSerializer(batches, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def raw_records_list(request):
    records = RawRecord.objects.all().order_by('-created_at')
    serializer = RawRecordSerializer(records, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def normalized_list(request):
    records = NormalizedActivity.objects.all().order_by('id')
    serializer = NormalizedActivitySerializer(records, many=True)

    data = serializer.data

    for row in data:
        quantity = row.get('quantity')

        row['is_suspicious'] = (
            row.get('activity_date') is None or
            quantity is None or
            quantity < 0 or
            quantity > 5000
        )

    return Response(data)


@api_view(['POST'])
def approve_activity(request, pk):
    try:
        activity = NormalizedActivity.objects.get(pk=pk)

        if activity.review_status in ["approved", "rejected"]:
            return Response(
                {"error": "This row has already been finalized."},
                status=400
            )

        # Debug print
        print(request.data)

        analyst_id = request.data.get(
            "analyst_id",
            "anauseranalyst@esg.com"
        )

        analyst_location = request.data.get(
            "analyst_location",
            "Unknown"
        )

        reason = request.data.get("reason", "")

        activity.review_status = "approved"
        activity.save()

        AuditLog.objects.create(
            activity=activity,
            analyst_id=analyst_id,
            analyst_location=analyst_location,
            action="approved",
            reason=reason,
        )

        return Response(
            {"message": "Activity approved successfully"}
        )

    except NormalizedActivity.DoesNotExist:
        return Response(
            {"error": "Activity not found"},
            status=404
        )


@api_view(['POST'])
def reject_activity(request, pk):
    try:
        activity = NormalizedActivity.objects.get(pk=pk)

        if activity.review_status in ["approved", "rejected"]:
            return Response(
                {"error": "This row has already been finalized."},
                status=400
            )

        # Debug print
        print(request.data)

        analyst_id = request.data.get(
            "analyst_id",
            "anauseranalyst@esg.com"
        )

        analyst_location = request.data.get(
            "analyst_location",
            "Unknown"
        )

        reason = request.data.get("reason", "")

        activity.review_status = "rejected"
        activity.save()

        AuditLog.objects.create(
            activity=activity,
            analyst_id=analyst_id,
            analyst_location=analyst_location,
            action="rejected",
            reason=reason,
        )

        return Response(
            {"message": "Activity rejected successfully"}
        )

    except NormalizedActivity.DoesNotExist:
        return Response(
            {"error": "Activity not found"},
            status=404
        )


@api_view(['GET'])
def audit_logs_list(request):
    logs = AuditLog.objects.all().order_by('-created_at')
    serializer = AuditLogSerializer(logs, many=True)
    return Response(serializer.data)