import re
from datetime import datetime
from typing import Dict, List

INVOICE_PREFIX = "09308000"

INVOICE_TYPE_MAP: Dict[str, str] = {
    "W": "weekly invoice",
    "WD": "weekly deferred invoice",
    "WH": "hazmat training invoice",
    "CH": "hazmat credit invoice",
    "C": "weekly MRA/misc credit memo",
    "CA": "weekly D2D obsolete credit memo",
    "CE": "parts exchange credit memo",
    "CF": "fleet credit memo",
    "CG": "weekly D2D guaranteed credit memo",
    "CI": "weekly ARO guaranteed parts returns",
    "CM": "weekly other guaranteed parts returns",
    "CP": "weekly D2D backorder credit memo",
    "WA": "AER invoice",
}

FCA_TO_INTERNAL_GL: Dict[str, Dict[str, str]] = {
    "ARC01012": {"gl_account": "604190", "label": "warranty chargebacks"},
    "ARC01217": {"gl_account": "704004", "label": "freight"},
    "ARC01222": {"gl_account": "704004", "label": "freight (dealer locator charge)"},
    "ARC01224": {"gl_account": "10400", "label": "parts (D2D obsolete)"},
    "ARC01226": {"gl_account": "101100", "label": "guaranteed backorder credit memo"},
    "ARC13309": {"gl_account": "101100", "label": "fleet credit memo / national fleet maintenance"},
    "ARC19000": {"gl_account": "10400", "label": "parts (battery core consolidation)"},
    "ARC31101": {"gl_account": "10400", "label": "parts (deposit part values)"},
    "ARC45012": {"gl_account": "704004", "label": "freight (transportation charge)"},
    "ARC08994": {"gl_account": "10400", "label": "parts (sheet metal repair)"},
    "ENV.CONTAINER": {"gl_account": "10400", "label": "parts (environmental container)"},
    "ENV.LUBRICANT": {"gl_account": "10400", "label": "parts (environmental lubricant)"},
}


HEADER_PATTERNS = [
    re.compile(r"MOPAR\s+CANADA\s+INC\.\s+-\s+PARTS\s+INVOICE", re.IGNORECASE),
    re.compile(r"AER\s+INVOICE", re.IGNORECASE),
]


def normalize_alnum(s: str) -> str:
    """Uppercase and strip everything that's not 0–9 or A–Z."""
    return re.sub(r"[^0-9A-Z]", "", s.upper())


def detect_invoice_start(text: str) -> bool:
    if not text:
        return False

    has_header = any(p.search(text) for p in HEADER_PATTERNS)
    has_invoice_number = "INVOICE NUMBER" in text.upper()
    return has_header and has_invoice_number


def _parse_invoice_date(raw_date: str) -> str:
    raw_date = raw_date.strip()
    try:
        # Normalize casing to handle uppercase month names.
        parsed = datetime.strptime(raw_date.title(), "%B %d, %Y")
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        return ""


def parse_invoice_metadata(first_page_text: str) -> Dict:
    invoice_number_match = re.search(r"INVOICE\s+NUMBER\s*:\s*([0-9A-Z\s]+)", first_page_text, re.IGNORECASE)
    invoice_date_match = re.search(r"INVOICE\s+DATE\s*:\s*([A-Z\s,0-9]+)", first_page_text, re.IGNORECASE)

    invoice_number_raw = invoice_number_match.group(1).strip() if invoice_number_match else ""
    invoice_date_raw = invoice_date_match.group(1).strip() if invoice_date_match else ""

    invoice_number_norm = normalize_alnum(invoice_number_raw)
    if not invoice_number_norm.startswith(INVOICE_PREFIX):
        raise ValueError("Invoice number missing expected prefix")

    remainder = invoice_number_norm[len(INVOICE_PREFIX) :]
    type_code_match = re.match(r"([A-Z]{1,2})([0-9]+)", remainder)
    if not type_code_match:
        raise ValueError("Could not parse invoice type code")

    invoice_type_code = type_code_match.group(1)
    invoice_number_digits = type_code_match.group(2)
    invoice_key_norm = f"{invoice_type_code}{invoice_number_digits}"
    invoice_type_desc = INVOICE_TYPE_MAP.get(invoice_type_code, "unknown")

    return {
        "invoice_number_raw": invoice_number_raw,
        "invoice_number_norm": invoice_number_norm,
        "invoice_type_code": invoice_type_code,
        "invoice_type_desc": invoice_type_desc,
        "invoice_key_norm": invoice_key_norm,
        "invoice_date_raw": invoice_date_raw,
        "invoice_date_iso": _parse_invoice_date(invoice_date_raw),
    }


def parse_summary(summary_text: str) -> Dict:
    lines = [line.strip() for line in summary_text.splitlines() if line.strip()]

    totals: Dict[str, float] = {}
    accounts: List[Dict] = []
    tax: Dict[str, float] = {"gst_hst_amount": 0.0, "gst_hst_rate": 0.0}

    account_pattern = re.compile(r"^([A-Z0-9.]+)\s+(.*\S)\s+([0-9,]+\.\d{2})$")
    amount_pattern = re.compile(r"^(TOTAL.*|DISCOUNTS\s+EARNED.*|NET\s+INVOICE\s+AMOUNT.*|NET\s+AMOUNT.*|.*TOTAL.*)\s+([0-9,]+\.\d{2})$",
                                re.IGNORECASE)
    gst_pattern = re.compile(r"GST/HST.*?@\s*([0-9.]+)%[^0-9]*([0-9,]+\.\d{2})", re.IGNORECASE)

    for line in lines:
        gst_match = gst_pattern.search(line)
        if gst_match:
            tax["gst_hst_rate"] = float(gst_match.group(1))
            tax["gst_hst_amount"] = float(gst_match.group(2).replace(",", ""))
            continue

        account_match = account_pattern.match(line)
        if account_match:
            code_raw, desc_raw, amount_raw = account_match.groups()
            accounts.append(
                {
                    "fca_code_raw": code_raw,
                    "fca_code_norm": normalize_alnum(code_raw),
                    "description_raw": desc_raw,
                    "description_norm": normalize_alnum(desc_raw),
                    "amount": float(amount_raw.replace(",", "")),
                }
            )
            continue

        amount_match = amount_pattern.match(line)
        if amount_match:
            label, amount_raw = amount_match.groups()
            totals[normalize_alnum(label)] = float(amount_raw.replace(",", ""))
            continue

    return {"totals": totals, "accounts": accounts, "tax": tax}


def _map_gst_account(amount: float) -> str:
    return "201105" if amount >= 0 else "201100"


def map_accounts_to_internal(summary_data: Dict) -> List[Dict]:
    mapped: List[Dict] = []

    for account in summary_data.get("accounts", []):
        mapping = FCA_TO_INTERNAL_GL.get(account["fca_code_raw"], None)
        mapped.append(
            {
                "fca_code": account["fca_code_raw"],
                "fca_description": account["description_raw"],
                "fca_amount": account["amount"],
                "internal_gl_account": mapping.get("gl_account") if mapping else None,
                "internal_label": mapping.get("label") if mapping else None,
            }
        )

    tax_amount = summary_data.get("tax", {}).get("gst_hst_amount", 0.0)
    if tax_amount != 0:
        mapped.append(
            {
                "fca_code": "GST/HST",
                "fca_description": "GST/HST tax",
                "fca_amount": tax_amount,
                "internal_gl_account": _map_gst_account(tax_amount),
                "internal_label": "tax payable" if tax_amount >= 0 else "tax credit",
            }
        )

    return mapped
