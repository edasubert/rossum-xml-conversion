import base64

import httpx
import pytest
from fastapi.testclient import TestClient

from xml_conversion.main import app, settings

# mock settings
settings.username = "username"
settings.password = "password"
settings.rossum_api_token = "token"
settings.rossum_api_url_template = (
    "https://rossum.api/queues/{queue_id}?id={annotation_id}"
)
settings.postbin_url = "https://post.bin"

rossum_document = """<?xml version="1.0" encoding="utf-8"?>
<export>
    <datapoint schema_id="invoice_id">143453775</datapoint>
    <datapoint schema_id="date_issue">2019-03-01</datapoint>
    <section schema_id="line_items_section">
        <tuple>
            <datapoint schema_id="item_description">description</datapoint>
        </tuple>
        <tuple>
            <datapoint schema_id="item_quantity">4</datapoint>
        </tuple>
    </section>
</export>"""

formatted_document = """<?xml version='1.0' encoding='utf-8'?>
<InvoiceRegisters><Invoices><Payable><InvoiceNumber>143453775</InvoiceNumber><InvoiceDate>2019-03-01 00:00:00</InvoiceDate><DueDate /><TotalAmount /><Notes /><Iban /><Amount /><Currency /><Vendor /><VendorAddress /><Details><Detail><Amount /><AccountId /><Quantity /><Notes>description</Notes></Detail><Detail><Amount /><AccountId /><Quantity>4</Quantity><Notes /></Detail></Details></Payable></Invoices></InvoiceRegisters>"""


client = TestClient(app)


def test_export(httpx_mock):
    httpx_mock.add_response(
        url="https://rossum.api/queues/10?id=222",
        match_headers={"Authorization": "token"},
        text=rossum_document,
    )

    httpx_mock.add_response(
        url="https://post.bin",
        match_json={
            "annotationId": 222,
            "content": base64.b64encode(bytes(formatted_document, "utf-8")).decode(
                "utf-8"
            ),
        },
    )

    auth = httpx.BasicAuth(username="username", password="password")
    response = client.get(f"/export?queue_id=10&annotation_id=222", auth=auth)

    assert response.status_code == 200
    assert response.json() == {"success": True}
