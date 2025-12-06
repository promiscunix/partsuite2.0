from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, DetailView, CreateView

from accounts.models import User
from invoices.models import Invoice, InvoiceLine
from receipts.models import ReceiptUpload
from returns.models import ReturnRequest
from service_requests.models import ServiceRequest
from sales.models import DueBillRequest
from .forms import (
  InvoiceCreateForm,
  InvoiceLineForm,
  ReceiptUploadForm,
  ReturnRequestForm,
  ServiceRequestForm,
  ServiceRequestCommentForm,
  DueBillRequestForm,
  DueBillItemForm,
  DueBillCommentForm,
)
from web.decorators import role_required


class DashboardView(LoginRequiredMixin, TemplateView):
  template_name = "dashboard.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx["stats"] = {
      "invoices": Invoice.objects.count(),
      "returns": ReturnRequest.objects.count(),
      "service_requests": ServiceRequest.objects.count(),
      "due_bills": DueBillRequest.objects.count(),
    }
    return ctx


@method_decorator(role_required([User.Role.ADMIN, User.Role.PARTS, User.Role.ACCOUNTING]), name="dispatch")
class InvoiceListView(LoginRequiredMixin, ListView):
  model = Invoice
  paginate_by = 25
  template_name = "invoices/list.html"
  ordering = ["-invoice_date", "-created_at"]


@method_decorator(role_required([User.Role.ADMIN, User.Role.PARTS, User.Role.ACCOUNTING]), name="dispatch")
class InvoiceDetailView(LoginRequiredMixin, DetailView):
  model = Invoice
  template_name = "invoices/detail.html"


@method_decorator(role_required([User.Role.ADMIN, User.Role.PARTS, User.Role.ACCOUNTING]), name="dispatch")
class InvoiceCreateView(LoginRequiredMixin, CreateView):
  model = Invoice
  form_class = InvoiceCreateForm
  template_name = "invoices/form.html"

  def form_valid(self, form):
    form.instance.uploaded_by = self.request.user
    messages.success(self.request, "Invoice created.")
    return super().form_valid(form)

  def get_success_url(self):
    return reverse("invoice-detail", args=[self.object.pk])


@method_decorator(role_required([User.Role.ADMIN, User.Role.PARTS, User.Role.ACCOUNTING]), name="dispatch")
class InvoiceLineCreateView(LoginRequiredMixin, CreateView):
  model = InvoiceLine
  form_class = InvoiceLineForm
  template_name = "invoices/line_form.html"

  def dispatch(self, request, *args, **kwargs):
    self.invoice = Invoice.objects.get(pk=kwargs["invoice_pk"])
    return super().dispatch(request, *args, **kwargs)

  def form_valid(self, form):
    form.instance.invoice = self.invoice
    messages.success(self.request, "Line added.")
    return super().form_valid(form)

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx["invoice"] = self.invoice
    return ctx

  def get_success_url(self):
    return reverse("invoice-detail", args=[self.invoice.pk])


@method_decorator(role_required([User.Role.ADMIN, User.Role.PARTS]), name="dispatch")
class ReceiptListView(LoginRequiredMixin, ListView):
  model = ReceiptUpload
  paginate_by = 25
  template_name = "receipts/list.html"
  ordering = ["-created_at"]


@method_decorator(role_required([User.Role.ADMIN, User.Role.PARTS]), name="dispatch")
class ReceiptCreateView(LoginRequiredMixin, CreateView):
  model = ReceiptUpload
  form_class = ReceiptUploadForm
  template_name = "receipts/form.html"

  def form_valid(self, form):
    form.instance.uploaded_by = self.request.user
    messages.success(self.request, "Receipt upload logged.")
    return super().form_valid(form)

  def get_success_url(self):
    return reverse("receipt-list")


@method_decorator(role_required([User.Role.ADMIN, User.Role.PARTS]), name="dispatch")
class ReturnListView(LoginRequiredMixin, ListView):
  model = ReturnRequest
  paginate_by = 25
  template_name = "returns/list.html"
  ordering = ["-created_at"]


@method_decorator(role_required([User.Role.ADMIN, User.Role.PARTS]), name="dispatch")
class ReturnCreateView(LoginRequiredMixin, CreateView):
  model = ReturnRequest
  form_class = ReturnRequestForm
  template_name = "returns/form.html"

  def form_valid(self, form):
    form.instance.created_by = self.request.user
    messages.success(self.request, "Return request created.")
    return super().form_valid(form)

  def get_success_url(self):
    return reverse("return-list")


@method_decorator(role_required([User.Role.ADMIN, User.Role.SERVICE, User.Role.PARTS]), name="dispatch")
class ServiceRequestListView(LoginRequiredMixin, ListView):
  model = ServiceRequest
  paginate_by = 25
  template_name = "service/list.html"
  ordering = ["-created_at"]


@method_decorator(role_required([User.Role.ADMIN, User.Role.SERVICE, User.Role.PARTS]), name="dispatch")
class ServiceRequestDetailView(LoginRequiredMixin, DetailView):
  model = ServiceRequest
  template_name = "service/detail.html"


@method_decorator(role_required([User.Role.ADMIN, User.Role.SERVICE, User.Role.PARTS]), name="dispatch")
class ServiceRequestCreateView(LoginRequiredMixin, CreateView):
  model = ServiceRequest
  form_class = ServiceRequestForm
  template_name = "service/form.html"

  def form_valid(self, form):
    form.instance.created_by = self.request.user
    messages.success(self.request, "Service request created.")
    return super().form_valid(form)

  def get_success_url(self):
    return reverse("service-detail", args=[self.object.pk])


@role_required([User.Role.ADMIN, User.Role.SERVICE, User.Role.PARTS])
def service_comment_add(request, pk):
  if request.method != "POST":
    return redirect("service-detail", pk=pk)
  req = ServiceRequest.objects.get(pk=pk)
  form = ServiceRequestCommentForm(request.POST)
  if form.is_valid():
    comment = form.save(commit=False)
    comment.request = req
    comment.author = request.user
    comment.save()
    messages.success(request, "Comment added.")
  else:
    messages.error(request, "Could not add comment.")
  return redirect("service-detail", pk=pk)


@method_decorator(role_required([User.Role.ADMIN, User.Role.SALES, User.Role.PARTS]), name="dispatch")
class DueBillListView(LoginRequiredMixin, ListView):
  model = DueBillRequest
  paginate_by = 25
  template_name = "sales/list.html"
  ordering = ["-created_at"]


@method_decorator(role_required([User.Role.ADMIN, User.Role.SALES, User.Role.PARTS]), name="dispatch")
class DueBillDetailView(LoginRequiredMixin, DetailView):
  model = DueBillRequest
  template_name = "sales/detail.html"


@method_decorator(role_required([User.Role.ADMIN, User.Role.SALES, User.Role.PARTS]), name="dispatch")
class DueBillCreateView(LoginRequiredMixin, CreateView):
  model = DueBillRequest
  form_class = DueBillRequestForm
  template_name = "sales/form.html"

  def form_valid(self, form):
    form.instance.requested_by = self.request.user
    messages.success(self.request, "Due bill created.")
    return super().form_valid(form)

  def get_success_url(self):
    return reverse("sales-detail", args=[self.object.pk])


@role_required([User.Role.ADMIN, User.Role.SALES, User.Role.PARTS])
def duebill_item_add(request, pk):
  if request.method != "POST":
    return redirect("sales-detail", pk=pk)
  req = DueBillRequest.objects.get(pk=pk)
  form = DueBillItemForm(request.POST)
  if form.is_valid():
    item = form.save(commit=False)
    item.request = req
    item.save()
    messages.success(request, "Item added.")
  else:
    messages.error(request, "Could not add item.")
  return redirect("sales-detail", pk=pk)


@role_required([User.Role.ADMIN, User.Role.SALES, User.Role.PARTS])
def duebill_comment_add(request, pk):
  if request.method != "POST":
    return redirect("sales-detail", pk=pk)
  req = DueBillRequest.objects.get(pk=pk)
  form = DueBillCommentForm(request.POST)
  if form.is_valid():
    comment = form.save(commit=False)
    comment.request = req
    comment.author = request.user
    comment.save()
    messages.success(request, "Comment added.")
  else:
    messages.error(request, "Could not add comment.")
  return redirect("sales-detail", pk=pk)
