from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from django.db.models import Q # Import Q for complex queries

# Using settings.AUTH_USER_MODEL is the best practice for ForeignKey to User
User = settings.AUTH_USER_MODEL 

class Conversation(models.Model):
    participant1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_p1')
    participant2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_p2')
    participants = models.ManyToManyField(User, related_name='conversations')
    last_message_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('participant1', 'participant2')
        indexes = [
            models.Index(fields=['last_message_timestamp']),
        ]

    def __str__(self):
        return f"Chat between {self.participant1.username} and {self.participant2.username}"

    def save(self, *args, **kwargs):
        """
        Custom save method to ensure participant order for unique_together.
        Always store participant1 as the user with the smaller ID.
        """
        if self.participant1_id is not None and self.participant2_id is not None:
            if self.participant1_id > self.participant2_id:
                self.participant1, self.participant2 = self.participant2, self.participant1
        super().save(*args, **kwargs)

    @classmethod
    def get_or_create_conversation(cls, user1, user2):
        # This method is fine as it's a class method and not directly
        # part of instance saving during migration generation.
        if user1.id > user2.id:
            user1, user2 = user2, user1
        
        conversation = cls.objects.filter(
            (Q(participant1=user1) & Q(participant2=user2))
        ).first()

        if not conversation:
            conversation = cls.objects.create(participant1=user1, participant2=user2)
        return conversation

class Message(models.Model):
    """
    Represents an individual message within a conversation.
    The recipient is implied by the conversation participants.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="The conversation this message belongs to."
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text="The user who sent this message."
    )
    # Removed 'recipient' field - it's implied by the Conversation
    # Removed 'subject' field - not common for chat messages
    body = models.TextField(help_text="The content of the message.")
    is_read = models.BooleanField(default=False, help_text="Indicates if the message has been read by the recipient.")
    sent_at = models.DateTimeField(default=timezone.now, help_text="The timestamp when the message was sent.")

    class Meta:
        ordering = ['sent_at'] # Always order messages by time
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        indexes = [
            models.Index(fields=['sent_at']),
        ]

    def __str__(self):
        return f"Msg from {self.sender.username} in Conversation {self.conversation.id} at {self.sent_at.strftime('%H:%M')}"

    def save(self, *args, **kwargs):
        """
        Custom save method to update the last_message_timestamp
        on the related conversation when a new message is saved.
        """
        super().save(*args, **kwargs)
        self.conversation.last_message_timestamp = self.sent_at # Or timezone.now()
        self.conversation.save(update_fields=['last_message_timestamp'])


# --- Existing Models (No Changes) ---
# models.py
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# core/models.py
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class SEO(models.Model):
    PAGE_TYPES = (
        ('home', 'Home Page'),
        ('service', 'Service'),
        ('course', 'Course'),
        ('blog', 'Blog Post'),
        ('about', 'About Page'),
        ('contact', 'Contact Page'),
        ('quote', 'Quote Request'),
        ('booking', 'Booking'),
        ('faq', 'FAQ'),
        ('other', 'Other'),
    )
    
    CONTENT_TYPES = (
        ('website', 'Website'),
        ('article', 'Article'),
        ('service', 'Service'),
        ('course', 'Course'),
    )
    
    # Primary meta
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES, default='service')
    meta_title = models.CharField(max_length=60)
    meta_description = models.CharField(max_length=160)
    meta_keywords = models.TextField()
    canonical_url = models.URLField(max_length=500, blank=True)
    robots_meta = models.CharField(max_length=200, default='index, follow')
    
    # Content association
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Open Graph
    og_title = models.CharField(max_length=60, blank=True)
    og_description = models.CharField(max_length=160, blank=True)
    og_image_url = models.URLField(blank=True)
    og_image_alt = models.CharField(max_length=100, blank=True)
    og_image_width = models.IntegerField(default=1200)
    og_image_height = models.IntegerField(default=630)
    og_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='website')
    
    # Twitter
    twitter_card = models.CharField(max_length=50, default='summary_large_image')
    twitter_site = models.CharField(max_length=100, default='@langtouch', blank=True)
    twitter_creator = models.CharField(max_length=100, default='@langtouch', blank=True)
    twitter_title = models.CharField(max_length=60, blank=True)
    twitter_description = models.CharField(max_length=160, blank=True)
    twitter_image_url = models.URLField(blank=True)
    
    # Organization
    organization_name = models.CharField(max_length=100, default='Langtouch')
    organization_phone = models.CharField(max_length=20, default='+255-123-456-789', blank=True)
    organization_logo = models.URLField(blank=True)
    
    # Address
    address_street = models.CharField(max_length=200, default='123 Language Street', blank=True)
    address_city = models.CharField(max_length=100, default='Dar es Salaam', blank=True)
    address_region = models.CharField(max_length=100, default='DSM', blank=True)
    address_postal = models.CharField(max_length=20, default='12345', blank=True)
    address_country = models.CharField(max_length=2, default='TZ', blank=True)
    
    # Social Media
    facebook_url = models.URLField(default='https://facebook.com/langtouch', blank=True)
    twitter_url = models.URLField(default='https://twitter.com/langtouch', blank=True)
    linkedin_url = models.URLField(default='https://linkedin.com/company/langtouch', blank=True)
    instagram_url = models.URLField(default='https://instagram.com/langtouch', blank=True)
    
    # Ratings & Pricing
    rating_value = models.DecimalField(max_digits=3, decimal_places=1, default=4.8)
    review_count = models.IntegerField(default=127)
    low_price = models.DecimalField(max_digits=10, decimal_places=2, default=50000, null=True, blank=True)
    high_price = models.DecimalField(max_digits=10, decimal_places=2, default=500000, null=True, blank=True)
    price_range = models.CharField(max_length=100, default='TZS 50,000 - 500,000', blank=True)
    
    # Service Area
    area_served = models.CharField(max_length=50, default='TZ', blank=True)
    area_served_name = models.CharField(max_length=100, default='Tanzania', blank=True)
    
    # Verification
    google_site_verification = models.CharField(max_length=100, blank=True)
    bing_site_verification = models.CharField(max_length=100, blank=True)
    yandex_site_verification = models.CharField(max_length=100, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'SEO Settings'
        verbose_name_plural = 'SEO Settings'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['page_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"SEO: {self.meta_title}"
    
    def save(self, *args, **kwargs):
        # Auto-generate og_title and twitter_title if empty
        if not self.og_title and self.meta_title:
            self.og_title = self.meta_title
        if not self.twitter_title and self.meta_title:
            self.twitter_title = self.meta_title
        
        # Auto-generate og_description and twitter_description if empty
        if not self.og_description and self.meta_description:
            self.og_description = self.meta_description
        if not self.twitter_description and self.meta_description:
            self.twitter_description = self.meta_description
            
        super().save(*args, **kwargs)
    
# core/models.py
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)

    # New fields
    reply = models.TextField(blank=True, null=True)
    replied = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} from {self.name}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('Info', 'Info'),
        ('Warning', 'Warning'),
        ('Success', 'Success'),
        ('Error', 'Error'),
    ]

    STATUS_CHOICES = [
        ('Unread', 'Unread'),
        ('Read', 'Read'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='Info')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unread')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.notification_type} - {self.user}"
    

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.score}★"