from django import forms
from .models import ContactMessage, Message, SEO, Notification
from .models import Rating


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        # Only include 'body' as it's the only remaining field to be filled by the user
        fields = ['body'] 
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'w-full p-3 bg-gray-800 text-white border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 transition duration-200 resize-none',
                'rows': 6,  # Adjust the number of rows as needed
                'placeholder': 'Write your message here...'
            }),
        }


class SEOForm(forms.ModelForm):
    class Meta:
        model = SEO
        fields = ['meta_title', 'meta_description', 'meta_keywords', 'canonical_url']

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['user', 'message', 'notification_type', 'status']





class RatingForm(forms.ModelForm):
    SCORE_CHOICES = [
        (1, "★☆☆☆☆ (1)"),
        (2, "★★☆☆☆ (2)"),
        (3, "★★★☆☆ (3)"),
        (4, "★★★★☆ (4)"),
        (5, "★★★★★ (5)"),
    ]

    score = forms.ChoiceField(
        choices=SCORE_CHOICES,
        widget=forms.RadioSelect(
            attrs={
                "class": "flex space-x-4 text-yellow-500 cursor-pointer"
            }
        ),
        label="Your Rating",
    )

    class Meta:
        model = Rating
        fields = ["score", "feedback"]
        widgets = {
            "feedback": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "w-full border-gray-300 rounded-lg shadow-sm p-3 focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Write your feedback...",
                }
            )
        }
        labels = {
            "feedback": "Your Feedback",
        }
