import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, PositiveInt
from pydantic_extra_types.currency_code import Currency as PydanticCurrency

DETAIL_SCHEMA_ID_2_TAG = {
    "item_description": "Notes",
    "item_quantity": "Quantity",
    "item_amount_total": "Amount",
}


class Detail(BaseModel):
    Amount: Optional[float] = None
    AccountId: Optional[int] = None
    Quantity: Optional[PositiveInt] = None
    Notes: Optional[str] = None


DOCUMENT_SCHEMA_ID_2_TAG = {
    "invoice_id": "InvoiceNumber",
    "date_issue": "InvoiceDate",
    "date_due": "DueDate",
    "amount_total": "TotalAmount",
    "iban": "Iban",
    "amount_total_tax": "Amount",
    "currency": "Currency",
    "sender_name": "Vendor",
    "sender_address": "VendorAddress",
}


# remove UpperCurrency, once this is merged: https://github.com/pydantic/pydantic-extra-types/pull/236
class UpperCurrency(PydanticCurrency):
    @classmethod
    def _validate(cls, currency_symbol: str, info) -> str:
        return super()._validate(currency_symbol.upper(), info)


class Document(BaseModel):
    InvoiceNumber: Optional[PositiveInt] = None
    InvoiceDate: Optional[datetime] = None
    DueDate: Optional[datetime] = None
    TotalAmount: Optional[float] = None
    Notes: Optional[str] = None
    Iban: Optional[str] = None
    Amount: Optional[float] = None
    Currency: Optional[UpperCurrency] = None
    Vendor: Optional[str] = None
    VendorAddress: Optional[str] = None


def clean_whitespace(string: str) -> str:
    return " ".join(string.split()).strip()


def parse_rossum_xml(text: str) -> tuple[Document, list[Detail]]:
    root = ET.fromstring(text)

    details = []
    for section in root.iter("section"):
        if section.attrib.get("schema_id") == "line_items_section":
            for detail in section.iter("tuple"):
                detail_fields = {}
                for datapoint in detail.iter("datapoint"):
                    if (schema_id := datapoint.attrib.get("schema_id")) is None:
                        continue
                    if (tag := DETAIL_SCHEMA_ID_2_TAG.get(schema_id)) is not None:
                        detail_fields[tag] = clean_whitespace(datapoint.text or "")
                details.append(Detail(**detail_fields))

    document_fields = {}
    for datapoint in root.iter("datapoint"):
        if (schema_id := datapoint.attrib.get("schema_id")) is None:
            continue
        if (tag := DOCUMENT_SCHEMA_ID_2_TAG.get(schema_id)) is not None:
            document_fields[tag] = clean_whitespace(datapoint.text or "")

    return Document(**document_fields), details


def build_xml(document: Document, details: list[Detail]) -> str:
    root = ET.Element("InvoiceRegisters")
    invoices_element = ET.SubElement(root, "Invoices")
    payable_element = ET.SubElement(invoices_element, "Payable")

    for tag, value in document:
        element = ET.SubElement(payable_element, tag)
        if value is not None:
            element.text = str(value)

    details_element = ET.SubElement(payable_element, "Details")
    for detail in details:
        detail_element = ET.SubElement(details_element, "Detail")
        for tag, value in detail:
            element = ET.SubElement(detail_element, tag)
            if value is not None:
                element.text = str(value)

    return ET.tostring(root, xml_declaration=True, encoding="unicode")


def convert_rossum_content(text: str) -> str:
    try:
        document, details = parse_rossum_xml(text)
    except ET.ParseError as e:
        raise ValueError from e

    return build_xml(document, details)
