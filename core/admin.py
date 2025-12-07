from django.contrib import admin
from django import forms
from django.urls import path
from django.shortcuts import render, redirect
from .models import SEO, ContactMessage, Notification
from .models import Message, Conversation

class ReplyForm(forms.Form):
    reply = forms.CharField(widget=forms.Textarea, required=True)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'body', 'is_read', 'sent_at']
    list_filter = ['is_read', 'sent_at', 'sender', 'conversation']
    search_fields = ['body']
    raw_id_fields = ['sender', 'conversation']

    change_form_template = "admin/messages/change_form_with_reply.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:message_id>/reply/', self.admin_site.admin_view(self.reply_to_message),
                 name='message-reply'),
        ]
        return custom_urls + urls

    def reply_to_message(self, request, message_id):
        message = Message.objects.get(id=message_id)
        if request.method == "POST":
            form = ReplyForm(request.POST)
            if form.is_valid():
                reply_text = form.cleaned_data['reply']
                # Create reply as a new Message in the same conversation
                Message.objects.create(
                    conversation=message.conversation,
                    sender=request.user,  # admin user
                    body=reply_text,
                    is_read=False
                )
                self.message_user(request, "Reply sent successfully.")
                return redirect(f"../../{message_id}/change/")
        else:
            form = ReplyForm()

        context = dict(
            self.admin_site.each_context(request),
            form=form,
            message=message,
        )
        return render(request, "admin/messages/reply_form.html", context)

# You should also register Conversation in admin if you haven't already
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'participant1', 'participant2', 'last_message_timestamp']
    list_filter = ['participant1', 'participant2']
    search_fields = ['participant1__username', 'participant2__username']
    raw_id_fields = ['participant1', 'participant2']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'received_at', 'replied']
    search_fields = ['name', 'email', 'subject', 'message']
    list_filter = ['received_at', 'replied']
    actions = ['mark_as_replied']

    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'subject', 'message')
        }),
        ('Admin Reply', {
            'fields': ('reply', 'replied'),
        }),
        ('Timestamps', {
            'fields': ('received_at',),
            'classes': ('collapse',)
        }),
    )

    def mark_as_replied(self, request, queryset):
        updated = queryset.update(replied=True)
        self.message_user(request, f"{updated} message(s) marked as replied.")
    mark_as_replied.short_description = "Mark selected messages as replied"


@admin.register(SEO)
class SEOAdmin(admin.ModelAdmin):
    list_display = ('meta_title', 'page_type', 'content_object_display', 'is_active', 'updated_at')
    list_filter = ('page_type', 'is_active', 'created_at')
    list_editable = ('is_active',)
    list_display_links = ('meta_title',)
    search_fields = ('meta_title', 'meta_description', 'meta_keywords')
    readonly_fields = ('created_at', 'updated_at')
    
    # Fieldsets for better organization
    fieldsets = (
        ('Basic Information', {
            'fields': ('page_type', 'meta_title', 'meta_description', 'meta_keywords', 'canonical_url', 'robots_meta', 'is_active')
        }),
        ('Content Association', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Open Graph', {
            'fields': ('og_title', 'og_description', 'og_type', 'og_image_url', 'og_image_alt', 'og_image_width', 'og_image_height'),
            'classes': ('collapse',)
        }),
        ('Twitter Card', {
            'fields': ('twitter_card', 'twitter_site', 'twitter_creator', 'twitter_title', 'twitter_description', 'twitter_image_url'),
            'classes': ('collapse',)
        }),
        ('Organization & Location', {
            'fields': ('organization_name', 'organization_phone', 'organization_logo', 
                      'address_street', 'address_city', 'address_region', 'address_postal', 'address_country',
                      'area_served', 'area_served_name'),
            'classes': ('collapse',)
        }),
        ('Social Media & Links', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url'),
            'classes': ('collapse',)
        }),
        ('Ratings & Pricing', {
            'fields': ('rating_value', 'review_count', 'low_price', 'high_price', 'price_range'),
            'classes': ('collapse',)
        }),
        ('Verification', {
            'fields': ('google_site_verification', 'bing_site_verification', 'yandex_site_verification'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Custom display method for content object
    def content_object_display(self, obj):
        if obj.content_object:
            return str(obj.content_object)[:50]
        return '—'
    content_object_display.short_description = 'Linked Content'
    
    # Custom actions
    actions = ['activate_seo', 'deactivate_seo']
    
    def activate_seo(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} SEO records activated.')
    activate_seo.short_description = 'Activate selected SEO records'
    
    def deactivate_seo(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} SEO records deactivated.')
    deactivate_seo.short_description = 'Deactivate selected SEO records'
    
    # Form customization
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Add help text
        form.base_fields['meta_title'].help_text = 'Keep under 60 characters for best SEO results'
        form.base_fields['meta_description'].help_text = 'Keep under 160 characters for best SEO results'
        form.base_fields['canonical_url'].help_text = 'Leave blank to use default URL'
        form.base_fields['og_image_url'].help_text = 'Recommended size: 1200x630 pixels'
        
        return form
    
    # Add preview button in change form
    change_form_template = 'admin/seo_change_form.html'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'notification_type', 'status', 'created_at']
    list_filter = ['notification_type', 'status', 'created_at']
    search_fields = ['user__email', 'message']
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(status='read')
        self.message_user(request, f"{updated} notification(s) marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"
