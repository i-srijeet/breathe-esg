import json
from datetime import datetime

import pandas as pd

from .models import ImportBatch, RawRecord, NormalizedActivity


def clean_json_value(value):
    if pd.isna(value):
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def parse_any_date(value):
    if value is None or value == "":
        return None
    parsed = pd.to_datetime(value, errors="coerce", dayfirst=True)
    if pd.isna(parsed):
        return None
    return parsed.date()


def load_sap_data():
    df = pd.read_csv("sample_data/sap_fuel_procurement.csv")

    batch = ImportBatch.objects.create(
        source_type="sap",
        file_name="sap_fuel_procurement.csv",
        status="uploaded",
    )

    for _, row in df.iterrows():
        cleaned_row = {k: clean_json_value(v) for k, v in row.to_dict().items()}

        RawRecord.objects.create(
            batch=batch,
            raw_data=cleaned_row,
            status="pending",
        )

    batch.status = "processed"
    batch.save()
    return batch


def load_utility_data():
    df = pd.read_csv("sample_data/utility_electricity.csv")

    batch = ImportBatch.objects.create(
        source_type="utility",
        file_name="utility_electricity.csv",
        status="uploaded",
    )

    for _, row in df.iterrows():
        cleaned_row = {k: clean_json_value(v) for k, v in row.to_dict().items()}

        RawRecord.objects.create(
            batch=batch,
            raw_data=cleaned_row,
            status="pending",
        )

    batch.status = "processed"
    batch.save()
    return batch


def load_travel_data():
    with open("sample_data/travel_itinerary.json", "r") as file:
        data = json.load(file)

    batch = ImportBatch.objects.create(
        source_type="travel",
        file_name="travel_itinerary.json",
        status="uploaded",
    )

    for row in data:
        cleaned_row = {k: clean_json_value(v) for k, v in row.items()}

        RawRecord.objects.create(
            batch=batch,
            raw_data=cleaned_row,
            status="pending",
        )

    batch.status = "processed"
    batch.save()
    return batch


def normalize_sap_records():
    raw_records = RawRecord.objects.filter(batch__source_type="sap")

    for record in raw_records:
        data = record.raw_data

        quantity = data.get("Quantity")
        if quantity is not None:
            try:
                quantity = float(quantity)
            except (TypeError, ValueError):
                quantity = None

        unit = data.get("Unit")
        normalized_unit = "L" if unit == "LTR" else unit

        activity_date = parse_any_date(data.get("Posting_Date"))

        review_status = "pending"
        if activity_date is None or quantity is None or quantity < 0 or quantity > 5000:
            review_status = "rejected"

        NormalizedActivity.objects.create(
            source_type="sap",
            activity_date=activity_date,
            category=data.get("Fuel_Type"),
            quantity=quantity,
            unit=unit,
            normalized_quantity=quantity,
            normalized_unit=normalized_unit,
            emissions=0,
            scope='Scope 1',
            review_status=review_status,
            raw_record=record,
        )


def normalize_utility_records():
    raw_records = RawRecord.objects.filter(batch__source_type="utility")

    for record in raw_records:
        data = record.raw_data

        quantity = data.get("kWh_Usage")
        if quantity is not None:
            try:
                quantity = float(quantity)
            except (TypeError, ValueError):
                quantity = None

        activity_date = parse_any_date(data.get("Billing_Start"))

        review_status = "pending"
        if activity_date is None or quantity is None or quantity < 0 or quantity > 50000:
            review_status = "rejected"

        NormalizedActivity.objects.create(
            source_type="utility",
            activity_date=activity_date,
            category="Electricity",
            quantity=quantity,
            unit="kWh",
            normalized_quantity=quantity,
            normalized_unit="kWh",
            emissions=0,
            scope="Scope 2",
            review_status=review_status,
            raw_record=record,
        )


def normalize_travel_records():
    raw_records = RawRecord.objects.filter(batch__source_type="travel")

    for record in raw_records:
        data = record.raw_data

        category = data.get("category", "Travel")
        activity_date = parse_any_date(data.get("travel_date"))

        quantity = None
        unit = "km"

        if category == "Hotel":
            quantity = data.get("nights")
            unit = "night"
        else:
            quantity = data.get("distance_km")
            unit = "km"

        if quantity is not None:
            try:
                quantity = float(quantity)
            except (TypeError, ValueError):
                quantity = None

        review_status = "pending"
        if activity_date is None or quantity is None or quantity < 0:
            review_status = "rejected"

        NormalizedActivity.objects.create(
            source_type="travel",
            activity_date=activity_date,
            category=category,
            quantity=quantity,
            unit=unit,
            normalized_quantity=quantity,
            normalized_unit=unit,
            emissions=0,
            scope='Scope 3',
            review_status=review_status,
            raw_record=record,
        )


def reset_demo_data():
    NormalizedActivity.objects.all().delete()
    RawRecord.objects.all().delete()
    ImportBatch.objects.all().delete()