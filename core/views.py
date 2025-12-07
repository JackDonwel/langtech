# views_fixed.py

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.conf import settings
import os
import json
import logging

from .models import ContactMessage, Message, Conversation, Rating, User
from .forms import ContactMessageForm, MessageForm, RatingForm

logger = logging.getLogger(__name__)

# ================================================================
#  Google Generative AI Import (Safe)
# ================================================================
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except Exception as e:
    GENAI_AVAILABLE = False
    logger.warning("google.generativeai not available: %s", e)


# ================================================================
#  API Key Helper
# ================================================================
def get_gemini_api_key():
    """Load Gemini API key from Django settings or environment."""
    return getattr(settings, "GEMINI_API_KEY", None) or os.environ.get("GEMINI_API_KEY")


# ================================================================
#  Gemini Normal Service (Stable)
# ================================================================
class GeminiService:
    """Standard Gemini 2.0 Flash AI responder."""

    def __init__(self):
        self.api_key = get_gemini_api_key()
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set.")

        if not GENAI_AVAILABLE:
            raise RuntimeError("google.generativeai SDK not installed.")

        try:
            genai.configure(api_key=self.api_key)

            self.model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 512,
                }
            )
        except Exception as e:
            logger.exception("Failed to initialize Gemini: %s", e)
            raise

        self.system_prompt = (
            "You are LangTouch AI Assistant. You help with translation, language learning, "
            "grammar explanations, and cultural context in a professional and friendly tone."
        )

    # -----------------------------
    # Generate AI Response
    # -----------------------------
    def get_ai_response(self, user_message, context_history=None):
        try:
            parts = [self.system_prompt]

            if context_history:
                for msg in context_history:
                    role = "User" if msg.get("role") == "user" else "Assistant"
                    parts.append(f"{role}: {msg.get('content')}")

            parts.append(f"User: {user_message}")
            prompt = "\n".join(parts)

            response = self.model.generate_content(prompt)

            if hasattr(response, "text"):
                return response.text

            return "Sorry — I couldn't generate a response."

        except Exception as e:
            logger.exception("Gemini response error: %s", e)
            return f"AI Service Error: {str(e)[:200]}"


# ================================================================
#  Gemini Streaming Service (Typing Effect)
# ================================================================
class GeminiStreamService:
    def __init__(self):
        api_key = getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            raise ValueError("GEMINI_API_KEY missing in settings")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def stream(self, prompt):
        try:
            stream = self.model.generate_content(
                prompt,
                stream=True
            )
            for chunk in stream:
                if hasattr(chunk, "text") and chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.exception("Gemini streaming error: %s", e)
            yield f"[Error: {str(e)}]"


# ================================================================
#  AI User (Bot Identity)
# ================================================================
def get_ai_user():
    ai_user, created = User.objects.get_or_create(
        username="langtouch_ai",
        defaults={
            "email": "ai@langtouch.com",
            "first_name": "LangTouch",
            "last_name": "AI Assistant",
            "is_active": True,
            "is_staff": False,
            "is_superuser": False,
        },
    )

    if created:
        ai_user.set_unusable_password()
        ai_user.save()

    return ai_user


# ================================================================
#  Gemini API Test View
# ================================================================
def test_gemini_api(request):
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=403)

    api_key = get_gemini_api_key()

    results = {
        "api_key_set": bool(api_key),
        "api_key_preview": f"{api_key[:10]}..." if api_key else "Not set",
        "test_results": [],
    }

    if not GENAI_AVAILABLE:
        results["test_results"].append({
            "status": "❌ SDK Missing",
            "error": "google.generativeai not installed."
        })
        return JsonResponse(results)

    if not api_key:
        results["test_results"].append({
            "status": "❌ Missing API Key",
            "error": "GEMINI_API_KEY not set."
        })
        return JsonResponse(results)

    # Run test
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        response = model.generate_content("Say 'Hello from Gemini!' in 5 words or less.")

        if getattr(response, "text", None):
            results["test_results"].append({
                "status": "✅ Success",
                "model": "gemini-2.0-flash",
                "response": response.text
            })
        else:
            results["test_results"].append({
                "status": "❌ Empty Response",
                "model": "gemini-2.0-flash",
                "error": "No text returned."
            })

    except Exception as e:
        results["test_results"].append({
            "status": "❌ Error",
            "model": "gemini-2.0-flash",
            "error": str(e)
        })

    return JsonResponse(results)

#=======================================================================
# Conversation helper (fallback if model doesn't have a helper)
#=======================================================================
def create_or_get_conversation(user_a, user_b):
    """Ensure a single Conversation for a pair of users, order-insensitive."""
    if user_a.id <= user_b.id:
        p1, p2 = user_a, user_b
    else:
        p1, p2 = user_b, user_a
    conversation, created = Conversation.objects.get_or_create(
        participant1=p1, participant2=p2,
        defaults={"last_message_timestamp": None}  # adjust per your model fields
    )
    return conversation, created

# ---------------------------
# Basic Views (unchanged except defensive tweaks)
# ---------------------------
def index_view(request):
    return render(request, "core/index.html")

def about_view(request):
    existing_rating = None
    try:
        existing_rating = Rating.objects.filter(user=request.user).first()
    except Exception:
        existing_rating = None

    if request.method == "POST" and not existing_rating:
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.save()
            return redirect("core:about")
    else:
        form = RatingForm() if not existing_rating else None

    ratings = Rating.objects.all().order_by("-created_at")[:6]
    for r in ratings:
        r.filled_stars = range(r.score)
        r.empty_stars = range(5 - r.score)

    return render(
        request,
        "core/about.html",
        {"form": form, "ratings": ratings, "existing_rating": existing_rating},
    )

def services_view(request):
    return render(request, "core/services.html")

def contact_form(request):
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("contact_success")
    else:
        form = ContactMessageForm()
    return render(request, "core/contact_form.html", {"form": form})

# ---------------------------
# Inbox view (defensive)
# ---------------------------
@login_required
def inbox(request):
    current_user = request.user
    ai_user = get_ai_user()

    conversations = Conversation.objects.filter(
        Q(participant1=current_user) | Q(participant2=current_user)
    ).order_by("-last_message_timestamp")

    selected_conversation = None
    other_participant = None
    messages = []
    is_ai_conversation = False

    if request.method == "POST":
        conversation_id = request.POST.get("conversation_id")
        body = (request.POST.get("body") or "").strip()
        if conversation_id and body:
            try:
                conversation = Conversation.objects.get(
                    Q(id=conversation_id)
                    & (Q(participant1=current_user) | Q(participant2=current_user))
                )
                user_message = Message.objects.create(
                    conversation=conversation, sender=current_user, body=body
                )

                if ai_user in [conversation.participant1, conversation.participant2]:
                    is_ai_conversation = True
                    message_history = conversation.messages.all().order_by("sent_at")
                    context_history = []
                    for msg in message_history:
                        role = "user" if msg.sender == current_user else "assistant"
                        context_history.append({"role": role, "content": msg.body})

                    try:
                        ai_service = GeminiService()
                        ai_response = ai_service.get_ai_response(body, context_history[-5:])
                    except Exception as e:
                        logger.exception("AI service unavailable: %s", e)
                        ai_response = f"AI Assistant is currently unavailable. ({str(e)})"

                    Message.objects.create(conversation=conversation, sender=ai_user, body=ai_response)

                return redirect(f"{request.path}?conversation_id={conversation.id}")
            except Conversation.DoesNotExist:
                logger.warning("Conversation does not exist: %s", conversation_id)
            except Exception as e:
                logger.exception("Error sending message: %s", e)

    selected_conversation_id = request.GET.get("conversation_id")
    if selected_conversation_id:
        try:
            selected_conversation = Conversation.objects.get(
                Q(id=selected_conversation_id)
                & (Q(participant1=current_user) | Q(participant2=current_user))
            )
            is_ai_conversation = ai_user in [selected_conversation.participant1, selected_conversation.participant2]
            other_participant = ai_user if is_ai_conversation else (
                selected_conversation.participant1 if selected_conversation.participant1 != current_user else selected_conversation.participant2
            )
            messages = selected_conversation.messages.all().order_by("sent_at")
        except Conversation.DoesNotExist:
            selected_conversation = None

    return render(
        request,
        "core/inbox.html",
        {
            "conversations": conversations,
            "selected_conversation": selected_conversation,
            "other_participant": other_participant,
            "messages": messages,
            "is_ai_conversation": is_ai_conversation,
            "ai_user": ai_user,
        },
    )

# ---------------------------
# Start AI conversation view (uses helper)
# ---------------------------
@login_required
def start_ai_conversation(request):
    current_user = request.user
    ai_user = get_ai_user()
    conversation, created = create_or_get_conversation(current_user, ai_user)

    if created:
        try:
            ai_service = GeminiService()
            welcome_message = ai_service.get_ai_response("Hello! I'm starting a conversation with you.")
        except Exception as e:
            logger.exception("AI welcome creation failed: %s", e)
            welcome_message = "Hello! I'm LangTouch AI Assistant. I'm here to help you with language learning. (AI service unavailable.)"

        Message.objects.create(conversation=conversation, sender=ai_user, body=welcome_message)

    return redirect(f"{reverse('core:inbox')}?conversation_id={conversation.id}")

# ---------------------------
# API endpoint for AI chat
# ---------------------------
@login_required
def api_ai_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_message = (data.get("message") or "").strip()
    if not user_message:
        return JsonResponse({"error": "Message is required"}, status=400)

    try:
        ai_service = GeminiService()
        ai_response = ai_service.get_ai_response(user_message)
    except Exception as e:
        logger.exception("AI service error: %s", e)
        return JsonResponse({"error": f"AI Service Error: {str(e)}", "status": "error"}, status=500)

    return JsonResponse({"response": ai_response, "status": "success"})

# Keep other views (sent_messages, send_message, contact_admin, test_gemini_api) mostly same but defensive.
@login_required
def sent_messages(request):
    messages = Message.objects.filter(sender=request.user).order_by("-sent_at")
    return render(request, "core/sent_messages.html", {"messages": messages})
# ===============================================================
# Send Message View (with AI integration)
# ===============================================================

@login_required
def send_message(request, conversation_id=None, recipient_username=None):
    current_user = request.user
    ai_user = get_ai_user()
    conversation = None
    other_user = None
    is_ai_conversation = False

    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if current_user not in [conversation.participant1, conversation.participant2]:
            return redirect("core:inbox")
        is_ai_conversation = ai_user in [conversation.participant1, conversation.participant2]
        other_user = ai_user if is_ai_conversation else (
            conversation.participant1 if conversation.participant2 == current_user else conversation.participant2
        )
    elif recipient_username:
        if recipient_username in ("ai_assistant", "langtouch_ai"):
            other_user = ai_user
            is_ai_conversation = True
        else:
            other_user = get_object_or_404(User, username=recipient_username)

        if other_user == current_user:
            return redirect("core:inbox")

        conversation, _ = create_or_get_conversation(current_user, other_user)
    else:
        return redirect("core:inbox")

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = current_user
            message.conversation = conversation
            message.save()

            if is_ai_conversation:
                message_history = conversation.messages.all().order_by("sent_at")
                context_history = []
                for msg in message_history:
                    role = "user" if msg.sender == current_user else "assistant"
                    context_history.append({"role": role, "content": msg.body})
                try:
                    ai_service = GeminiService()
                    ai_response = ai_service.get_ai_response(message.body, context_history[-5:])
                except Exception as e:
                    ai_response = f"AI Assistant is currently unavailable. Error: {str(e)}"
                Message.objects.create(conversation=conversation, sender=ai_user, body=ai_response)

            return redirect("core:inbox")
    else:
        form = MessageForm()

    return render(request, "core/send_message.html", {"form": form, "conversation": conversation, "other_user": other_user, "is_ai_conversation": is_ai_conversation})

@login_required
def contact_admin(request):
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        return render(request, "core/contact_admin.html", {"error": "No admin account found."})

    current_user = request.user
    conversation, _ = create_or_get_conversation(current_user, admin_user)

    if request.method == "POST":
        body = (request.POST.get("body") or "").strip()
        if body:
            Message.objects.create(conversation=conversation, sender=current_user, body=body)

    messages = conversation.messages.all().order_by("sent_at")
    return render(request, "core/contact_admin.html", {"admin_user": admin_user, "messages": messages, "conversation": conversation})


