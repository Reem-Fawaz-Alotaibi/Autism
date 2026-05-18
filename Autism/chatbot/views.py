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
    if not request.user.is_authenticated:
        return Response({"error": "login required"}, status=401)

    conv = Conversation.objects.create(user=request.user)
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

    # Create User message
    msg = ChatMessage.objects.create(
        conversation=conv,
        message_type='user',
        content=content
    )

    # Call OpenAI API to generate AI response
    try:
        from decouple import config
        from openai import OpenAI
        
        openai_api_key = config('OPENAI_API_KEY', default='')
        
        if openai_api_key:
            client = OpenAI(api_key=openai_api_key)
            
            system_prompt = (
                "أنت مساعد ذكي مخصص لمساعدة المتخصصين (وليس أولياء الأمور) في تحليل وفهم سلوكيات الأطفال المصابين بالتوحد. "
                "يجب عليك الالتزام بالقواعد التالية: "
                "1. عدم تشخيص حالة الطفل بأي شكل من الأشكال. "
                "2. عدم تقديم أي معلومات حساسة أو طبية خاصة. "
                "3. هذا الشات خاص بالمختصين فقط وليس مرتبطاً بولي الأمر، لذلك يمكنك التحدث بمصطلحات مهنية. "
                "4. التركيز على تقديم معلومات وأفكار تخص سلوك الطفل المتوحد بناءً على استفسارات المختص. "
                "5. إذا طُلب منك تشخيص أو تقديم دواء، اعتذر ووضح أن دورك هو تحليل السلوك فقط."
            )

            messages_for_ai = [
                {"role": "system", "content": system_prompt}
            ]

            # Fetch recent messages for context
            recent_messages = ChatMessage.objects.filter(conversation=conv).order_by('created_at')[:20]
            for m in recent_messages:
                role = 'user' if m.message_type == 'user' else 'assistant'
                messages_for_ai.append({"role": role, "content": m.content})
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_for_ai,
                max_tokens=1000,
            )
            ai_content = response.choices[0].message.content
        else:
            ai_content = "عذراً، لم يتم إعداد مفتاح API الخاص بـ OpenAI. يرجى إضافة OPENAI_API_KEY إلى ملف .env."

    except Exception as e:
        ai_content = f"حدث خطأ أثناء التواصل مع الذكاء الاصطناعي: {str(e)}"

    # Create AI message
    ai_msg = ChatMessage.objects.create(
        conversation=conv,
        message_type='ai',
        content=ai_content
    )

    return Response(ChatMessageSerializer(msg).data)


# API: get messages
@api_view(['GET'])
def get_messages(request, conv_id):
    messages = ChatMessage.objects.filter(
        conversation_id=conv_id
    ).order_by('created_at')

    return Response(ChatMessageSerializer(messages, many=True).data)