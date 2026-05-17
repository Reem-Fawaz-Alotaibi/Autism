from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import Http404, JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Conversation, ChatMessage
from .serializers import ChatMessageSerializer


# HTML Views
def chatbot_view(request):
    return render(request, 'chatbot/chatbot.html')

def chatbot_history(request):
    return render(request, 'chatbot/chatbot_history.html')

def chatbot_window(request):
    return render(request, 'chatbot/chatbot_window.html')


# API: get or create conversation
def get_or_create_conversation(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login required"}, status=401)
    
    conv, _ = Conversation.objects.get_or_create(user=request.user)
    return JsonResponse({"conv_id": conv.id})


# API: create conversation
@api_view(['POST'])
def create_conversation(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        user = User.objects.first()

    conv = Conversation.objects.create(user=user)
    return Response({"id": conv.id})


# API: send message
@api_view(['POST'])
def send_message(request, conv_id):
    content = request.data.get('content')

    if not content:
        return Response({"error": "content is required"}, status=400)

    try:
        conv = Conversation.objects.get(id=conv_id)
    except Conversation.DoesNotExist:
        raise Http404("Conversation not found")

    msg = ChatMessage.objects.create(
        conversation=conv,
        message_type='user',
        content=content
    )

    return Response(ChatMessageSerializer(msg).data)


# API: get messages
@api_view(['GET'])
def get_messages(request, conv_id):
    messages = ChatMessage.objects.filter(
        conversation_id=conv_id
    ).order_by('created_at')

    return Response(ChatMessageSerializer(messages, many=True).data)