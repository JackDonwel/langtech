# payments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import time, uuid
import qrcode
import io
from django.http import HttpResponse, HttpResponseBadRequest

from .forms import PaymentForm
from .models import PaymentTransaction, PaymentMethod, Payment
from quotes.models import QuoteRequest
from bookings.models import Booking
from content.models import Video
from lessons.models import Course
from payments.models import Currency
from django.conf import settings
from .forms import ReceiptUploadForm
from lessons.models import Course
from content.models import Video
from bookings.models import Booking
from quotes.models import QuoteRequest


# -------------------- GENERIC SELECT PAYMENT --------------------

@login_required
def select_payment_method(request, obj_type, obj_id):
    # Map object type to model + amount field
    model_map = {
        "course": (Course, "price"),
        "booking": (Booking, "amount"),
        "quote": (QuoteRequest, "amount"),
        "video": (Video, "price"),
    }

    if obj_type not in model_map:
        return render(request, "payments/error.html", {"message": "Invalid payment type"})

    model, amount_field = model_map[obj_type]
    obj = get_object_or_404(model, id=obj_id)
    amount = getattr(obj, amount_field, 0)

    # ✅ Ensure a Payment record exists (Pending by default)
    payment, created = Payment.objects.get_or_create(
        user=request.user,
        reference_number=f"TXN-{request.user.id}-{obj_type.upper()}-{obj_id}",
        defaults={
            "amount": amount,
            "currency": Currency.objects.filter(is_default=True).first(),
            "method": PaymentMethod.objects.first(),  # placeholder until chosen
            "status": "Pending",
            obj_type: obj,  # assign FK dynamically
        },
    )

    return render(request, "payments/select_method.html", {
        "object": obj,
        "type": obj_type,
        "amount": amount,
        "payment": payment,   # pass payment instance to template
        "mpesa_number": "68088449",
        "airtel_number": "",
    })

# -------------------- M-PESA PAYMENTS --------------------
@login_required
def pay_with_mpesa(request, obj_type, obj_id):  # Changed parameter names
    obj = _get_payment_object(obj_type, obj_id)  # Updated function call
    if not obj:
        messages.error(request, "Invalid payment object.")
        return redirect("home")

    # Create Payment
    tx_ref = f"MPESA-{uuid.uuid4().hex[:8]}"
    payment = Payment.objects.create(
        user=request.user,
        amount=getattr(obj, "price", getattr(obj, "amount", 0)),
        method=PaymentMethod.objects.filter(name__iexact="M-Pesa").first(),
        reference_number=tx_ref,
        status="Completed",  # Simulated
        currency=Currency.objects.filter(is_default=True).first()
    )

    # Create Transaction log
    PaymentTransaction.objects.create(
        payment=payment,
        provider_reference="SIMULATED_MPESA",
        provider_status="SUCCESS",
        provider_response="{'status': 'SUCCESS', 'provider': 'M-Pesa'}"
    )

    messages.success(request, f"M-Pesa payment completed for {obj_type} #{obj_id}")
    return redirect("payments:payment_success")


# -------------------- AIRTEL MONEY PAYMENTS --------------------
@login_required
def pay_with_airtel(request, obj_type, obj_id):  # Changed parameter names
    obj = _get_payment_object(obj_type, obj_id)  # Updated function call
    if not obj:
        messages.error(request, "Invalid payment object.")
        return redirect("home")

    # Create Payment
    tx_ref = f"AIRTEL-{uuid.uuid4().hex[:8]}"
    payment = Payment.objects.create(
        user=request.user,
        amount=getattr(obj, "price", getattr(obj, "amount", 0)),
        method=PaymentMethod.objects.filter(name__iexact="Airtel Money").first(),
        reference_number=tx_ref,
        status="Completed",  # Simulated
        currency=Currency.objects.filter(is_default=True).first()
    )

    # Create Transaction log
    PaymentTransaction.objects.create(
        payment=payment,
        provider_reference="SIMULATED_AIRTEL",
        provider_status="SUCCESS",
        provider_response="{'status': 'SUCCESS', 'provider': 'Airtel Money'}"
    )

    messages.success(request, f"Airtel Money payment completed for {obj_type} #{obj_id}")
    return redirect("payments:payment_success")


# -------------------- HELPERS --------------------
def _get_payment_object(obj_type, obj_id):  # Updated parameter names
    """Fetch the correct object for payment"""
    if obj_type == "course":
        return get_object_or_404(Course, id=obj_id)
    elif obj_type == "booking":
        return get_object_or_404(Booking, id=obj_id)
    elif obj_type == "quote":
        return get_object_or_404(QuoteRequest, id=obj_id)
    elif obj_type == "video":
        return get_object_or_404(Video, id=obj_id)
    return None


# -------------------- SUCCESS / HISTORY --------------------
def payment_success(request):
    return render(request, 'payments/payment_success.html')

@login_required
def payment_history(request):
    transactions = PaymentTransaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/history.html', {'transactions': transactions})

@login_required
def upload_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    if request.method == "POST":
        print("📤 POST request received")
        print("FILES:", request.FILES)

        form = ReceiptUploadForm(request.POST, request.FILES, instance=payment)
        if form.is_valid():
            print("✅ Form valid")
            payment = form.save(commit=False)
            payment.status = "Pending"
            payment.is_confirmed = False
            payment.save()
            return redirect("content:video_learning")
        else:
            print("❌ Form errors:", form.errors)
    else:
        form = ReceiptUploadForm(instance=payment)

    return render(request, "payments/upload_receipt.html", {"form": form, "payment": payment})

@login_required
def buy_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)

    # Pick default currency & method (you can let them choose)
    currency = Currency.objects.filter(is_default=True).first()
    method = PaymentMethod.objects.first()

    # Create a pending payment
    payment = Payment.objects.create(
        user=request.user,
        video=video,
        amount=video.price,
        currency=currency,
        method=method,
        reference_number=f"VID-{request.user.id}-{int(time.time())}",
        status="Pending",
    )

    # Redirect to receipt upload page
    return redirect("payments:upload_receipt", payment_id=payment.id)

# REMOVE THE DUPLICATE select_payment_method FUNCTION AT THE BOTTOM OF THE FILE


def generate_qr(request, obj_type, obj_id, method):
    """Generate QR code for payment (M-Pesa / Airtel)"""
    if obj_type == "video":
        obj = get_object_or_404(Video, id=obj_id)
        amount = obj.price
    elif obj_type == "course":
        obj = get_object_or_404(Course, id=obj_id)
        amount = obj.price
    elif obj_type == "booking":
        obj = get_object_or_404(Booking, id=obj_id)
        amount = obj.amount
    elif obj_type == "quote":
        obj = get_object_or_404(QuoteRequest, id=obj_id)
        amount = obj.amount
    else:
        return HttpResponseBadRequest("Invalid type")

    if method == "mpesa":
        number = "68088449"
    elif method == "airtel":
        number = "+255784567890"
    else:
        return HttpResponseBadRequest("Invalid method")

    # Create payment text
    qr_text = f"PAY TO {number} AMOUNT {amount} REFERENCE {obj_type.upper()}{obj.id}"

    # Generate QR image
    qr = qrcode.make(qr_text)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    return HttpResponse(buf.getvalue(), content_type="image/png")