import csv
import io
from datetime import datetime

REQUIRED_COLUMNS = [
    "transaction_id", "customer_id", "date",
    "description", "payee", "amount", "channel",
]


class CSVValidationError(Exception):
    """Raised when the uploaded CSV fails structural or content validation."""
    pass


def parse_transactions_csv(file_obj):
    """
    Parse and validate an uploaded transaction CSV.

    Args:
        file_obj: a file-like object (e.g. Django's UploadedFile).

    Returns:
        list[dict]: parsed transaction rows.

    Raises:
        CSVValidationError: on empty file, missing columns, no data rows,
            or any row-level validation failure.
    """
    raw_bytes = file_obj.read()
    if not raw_bytes or not raw_bytes.strip():
        raise CSVValidationError("The uploaded file is empty.")

    try:
        decoded = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise CSVValidationError("The uploaded file is not valid UTF-8 text.")

    reader = csv.DictReader(io.StringIO(decoded))

    if reader.fieldnames is None:
        raise CSVValidationError("The uploaded file has no header row.")

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
    if missing_columns:
        raise CSVValidationError(f"Missing required column(s): {', '.join(missing_columns)}")

    transactions = []
    errors = []

    for row_number, row in enumerate(reader, start=2):  # row 1 is the header
        transaction, row_errors = _parse_row(row, row_number)
        if row_errors:
            errors.extend(row_errors)
        else:
            transactions.append(transaction)

    if errors:
        raise CSVValidationError("; ".join(errors))

    if not transactions:
        raise CSVValidationError("The CSV file contains no transaction rows.")

    return transactions