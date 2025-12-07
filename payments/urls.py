from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path('select/<str:obj_type>/<int:obj_id>/', views.select_payment_method, name='select_payment_method'),
    path('pay/mpesa/<str:obj_type>/<int:obj_id>/', views.pay_with_mpesa, name='pay_with_mpesa'),
    path('pay/airtel/<str:obj_type>/<int:obj_id>/', views.pay_with_airtel, name='pay_with_airtel'),
    path("buy/video/<int:video_id>/", views.buy_video, name="buy_video"),

    # ✅ QR Code
    path('qr/<str:obj_type>/<int:obj_id>/<str:method>/', views.generate_qr, name='generate_qr'),
    path("receipt/upload/<int:payment_id>/", views.upload_receipt, name="upload_receipt"),
]
