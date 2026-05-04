import uuid
from django.db import models
# Create your models here.

class School(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, db_index=True)
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    logo = models.ImageField(upload_to='school_logos/', null=True, blank=True)
    academic_year = models.CharField(max_length=9, default='2025-26')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class SchoolSettings(models.Model):
    school = models.OneToOneField(
        School, on_delete=models.CASCADE, related_name="settings"
    )
    # Razorpay
    razorpay_key_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_key_secret = models.CharField(max_length=100, blank=True, null=True)
    razorpay_account_number = models.CharField(max_length=100, blank=True, null=True)
    upi_vpa = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. greenwood@razorpay")

    # Twilio / WhatsApp / SMS
    twilio_account_sid = models.CharField(max_length=100, blank=True, null=True)
    twilio_auth_token = models.CharField(max_length=100, blank=True, null=True)
    whatsapp_from = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. whatsapp:+14155238886")
    sms_from = models.CharField(max_length=50, blank=True, null=True)

    # Email
    default_from_email = models.EmailField(blank=True, null=True)

    # Reminder schedule — stored as JSON list e.g. [7, 3, 1]
    fee_reminder_days = models.JSONField(default=list, help_text="Days before due date to send reminders e.g. [7, 3, 1]")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings — {self.school.name}"
