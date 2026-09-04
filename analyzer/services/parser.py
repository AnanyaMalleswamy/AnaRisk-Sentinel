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
def _parse_row(row, row_number):
    errors = []

    transaction_id = (row.get("transaction_id") or "").strip()
    if not transaction_id:
        errors.append(f"Row {row_number}: missing transaction_id")

    customer_id = (row.get("customer_id") or "").strip()
    if not customer_id:
        errors.append(f"Row {row_number}: missing customer_id")

    date_str = (row.get("date") or "").strip()
    parsed_date = None
    if not date_str:
        errors.append(f"Row {row_number}: missing date")
    else:
        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            errors.append(f"Row {row_number}: invalid date '{date_str}' (expected YYYY-MM-DD)")

    description = (row.get("description") or "").strip()
    payee = (row.get("payee") or "").strip()

    amount_str = (row.get("amount") or "").strip()
    amount = None
    if not amount_str:
        errors.append(f"Row {row_number}: missing amount")
    else:
        try:
            amount = float(amount_str)
        except ValueError:
            errors.append(f"Row {row_number}: invalid amount '{amount_str}'")

    channel = (row.get("channel") or "").strip()
    if not channel:
        errors.append(f"Row {row_number}: missing channel")

    if errors:
        return None, errors

    transaction = {
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "date": parsed_date.isoformat(),
        "description": description,
        "payee": payee,
        "amount": amount,
        "channel": channel,
    }
    return transaction, []