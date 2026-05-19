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

    # Call AI API to generate response
    ai_content = ""
    try:
        from decouple import config
        import google.generativeai as genai
        
        gemini_api_key = config('GEMINI_API_KEY', default='')
        openai_api_key = config('OPENAI_API_KEY', default='')
        
        system_prompt = (
            "أنت مساعد ذكي مخصص لمساعدة المتخصصين (وليس أولياء الأمور) في تحليل وفهم سلوكيات الأطفال المصابين بالتوحد. "
            "يجب عليك الالتزام بالقواعد التالية: "
            "1. عدم تشخيص حالة الطفل بأي شكل من الأشكال. "
            "2. عدم تقديم أي معلومات حساسة أو طبية خاصة. "
            "3. هذا الشات خاص بالمختصين فقط وليس مرتبطاً بولي الأمر، لذلك يمكنك التحدث بمصطلحات مهنية. "
            "4. التركيز على تقديم معلومات وأفكار تخص سلوك الطفل المتوحد بناءً على استفسارات المختص. "
            "5. إذا طُلب منك تشخيص أو تقديم دواء، اعتذر ووضح أن دورك هو تحليل السلوك فقط."
        )

        recent_messages = ChatMessage.objects.filter(conversation=conv).order_by('created_at')[:20]

        # Flag to track if successfully generated
        generated = False

        # 1. Try Gemini
        if gemini_api_key and gemini_api_key != "your_gemini_api_key_here":
            try:
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel(
                    model_name='gemini-1.5-flash',
                    system_instruction=system_prompt
                )
                
                messages_for_gemini = []
                for m in recent_messages:
                    role = 'user' if m.message_type == 'user' else 'model'
                    messages_for_gemini.append({"role": role, "parts": [m.content]})
                
                response = model.generate_content(contents=messages_for_gemini)
                ai_content = response.text
                generated = True
            except Exception as e_gemini:
                # Fallback to OpenAI if Gemini fails
                pass

        # 2. Try OpenAI Fallback
        if not generated and openai_api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_api_key)
                
                messages_for_ai = [
                    {"role": "system", "content": system_prompt}
                ]
                for m in recent_messages:
                    role = 'user' if m.message_type == 'user' else 'assistant'
                    messages_for_ai.append({"role": role, "content": m.content})
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages_for_ai,
                    max_tokens=1000,
                )
                ai_content = response.choices[0].message.content
                generated = True
            except Exception as e_openai:
                ai_content = f"حدث خطأ أثناء التواصل مع الذكاء الاصطناعي (OpenAI): {str(e_openai)}"
        
        # 3. If neither worked
        if not generated:
            if not gemini_api_key or gemini_api_key == "your_gemini_api_key_here":
                if not openai_api_key:
                    ai_content = "عذراً، لم يتم إعداد مفاتيح API الخاصة بـ Gemini أو OpenAI. يرجى إضافة المفاتيح اللازمة إلى ملف .env."
                else:
                    ai_content = "عذراً، حدث خطأ أثناء محاولة الاتصال بـ Gemini، وجاري استخدام OpenAI كبديل ولكن يبدو أن هناك مشكلة."
            else:
                ai_content = "عذراً، فشل كلا النموذجين (Gemini و OpenAI) في الاستجابة. يرجى التحقق من صحة مفاتيح الـ API أو حالة الاتصال بالإنترنت."

    except Exception as e:
        ai_content = f"حدث خطأ غير متوقع: {str(e)}"

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