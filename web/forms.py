from datetime import timedelta

from django import forms

from invoices.models import Invoice, InvoiceLine
from receipts.models import ReceiptUpload
from returns.models import ReturnRequest
from service_requests.models import ServiceRequest, ServiceRequestComment
from sales.models import DueBillRequest, DueBillItem, DueBillComment


class InvoiceCreateForm(forms.ModelForm):
  class Meta:
    model = Invoice
    fields = ["supplier", "invoice_number", "invoice_date", "total_amount", "status", "billed_flag", "received_flag", "notes"]
    widgets = {
      "invoice_date": forms.DateInput(attrs={"type": "date"}),
      "notes": forms.Textarea(attrs={"rows": 3}),
    }


class InvoiceLineForm(forms.ModelForm):
  class Meta:
    model = InvoiceLine
    fields = ["part_number", "description", "quantity", "unit_price", "refund_status"]


class ReceiptUploadForm(forms.ModelForm):
  class Meta:
    model = ReceiptUpload
    fields = ["filename", "source", "notes"]
    widgets = {
      "notes": forms.Textarea(attrs={"rows": 3}),
    }


class ReturnRequestForm(forms.ModelForm):
  class Meta:
    model = ReturnRequest
    fields = ["invoice_line", "status", "reason", "rma_number", "refund_received_at"]
    widgets = {
      "refund_received_at": forms.DateInput(attrs={"type": "date"}),
      "reason": forms.Textarea(attrs={"rows": 3}),
    }


class ServiceRequestForm(forms.ModelForm):
  request_type = forms.ChoiceField(
    choices=ServiceRequest.RequestType.choices, label="Request Type"
  )
  warranty_type = forms.ChoiceField(
    choices=ServiceRequest.WarrantyType.choices, label="Warranty Type"
  )
  received_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Receive Date")

  class Meta:
    model = ServiceRequest
    fields = [
      "request_type",
      "part_number",
      "vin",
      "ro_number",
      "customer_name",
      "customer_number",
      "warranty_type",
      "ordered_date",
      "received_date",
      "expiry_date",
      "status",
      "assigned_to",
      "notes",
    ]
    widgets = {
      "ordered_date": forms.DateInput(attrs={"type": "date"}),
      "expiry_date": forms.DateInput(attrs={"type": "date", "readonly": True}),
      "notes": forms.Textarea(attrs={"rows": 3}),
    }

  def clean(self):
    cleaned_data = super().clean()
    received_date = cleaned_data.get("received_date")
    if received_date:
      cleaned_data["expiry_date"] = received_date + timedelta(days=30)
    return cleaned_data


class ServiceRequestCommentForm(forms.ModelForm):
  class Meta:
    model = ServiceRequestComment
    fields = ["body"]
    widgets = {"body": forms.Textarea(attrs={"rows": 2})}


class DueBillRequestForm(forms.ModelForm):
  class Meta:
    model = DueBillRequest
    fields = [
      "customer_name",
      "customer_number",
      "vin",
      "stock_number",
      "sales_consultant_name",
      "vehicle_info",
      "promised_date",
      "status",
      "assigned_to",
      "notes",
    ]
    widgets = {
      "promised_date": forms.DateInput(attrs={"type": "date"}),
      "notes": forms.Textarea(attrs={"rows": 3}),
    }


class DueBillItemForm(forms.ModelForm):
  class Meta:
    model = DueBillItem
    fields = ["description", "part_number", "status"]


class DueBillCommentForm(forms.ModelForm):
  class Meta:
    model = DueBillComment
    fields = ["body"]
    widgets = {"body": forms.Textarea(attrs={"rows": 2})}




class MultipleFileInput(forms.ClearableFileInput):
  allow_multiple_selected = True


class FCAInvoiceUploadForm(forms.Form):
  files = forms.FileField(
    label="Invoice PDFs",
    widget=MultipleFileInput(attrs={"multiple": True, "accept": "application/pdf"}),
  )
