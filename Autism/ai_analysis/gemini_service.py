import time
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def analyze_video(video_file_path):
    print("جاري رفع الفيديو إلى سيرفرات Gemini...")
    uploaded_file = client.files.upload(file=video_file_path)
    print(f"تم الرفع بنجاح. المعرف: {uploaded_file.name}")

    print("جاري معالجة الفيديو...")
    while True:
        file_info = client.files.get(name=uploaded_file.name)
        print(f"حالة الفيديو: {file_info.state.name}")

        if file_info.state.name == "ACTIVE":
            print("الفيديو جاهز للتحليل.")
            break
        elif file_info.state.name == "FAILED":
            raise Exception("فشلت معالجة الفيديو.")

        time.sleep(7)

    prompt = """
    أنت متخصص في تحليل سلوك أطفال طيف التوحد.
    راقب هذا الفيديو بدقة وأعطني تقريراً مفصلاً باللغة العربية يشمل:

    1. التواصل البصري:
       - هل يحافظ الطفل على التواصل البصري؟
       - هل يتجنب النظر للأشخاص أو الكاميرا؟

    2. الحساسية الحسية:
       - هل يضع يديه على أذنيه؟
       - هل يبدو متأثراً من أصوات أو ضوء في البيئة المحيطة؟
       - هل يتجنب لمس أشياء معينة؟

    3. السلوكيات التكرارية:
       - هل يكرر حركات مثل الرفرفة أو التأرجح أو الدوران؟
       - هل يرتب أشياء بشكل متكرر؟

    4. المهارات الحركية:
       - كيف يتحرك الطفل؟ هل حركته طبيعية أم فيها صعوبات؟
       - هل يمشي على أطراف أصابعه؟

    5. التواصل اللغوي:
       - هل يتكلم أو يصدر أصواتاً؟
       - هل يستجيب عند مناداته؟
       - هل يستخدم إيماءات للتواصل؟

    6. التفاعل الاجتماعي:
       - هل يتفاعل مع الأشخاص من حوله؟
       - هل يبادر بالتواصل أم ينعزل؟

    في النهاية، اذكر:
    - أبرز  ملاحظات سلوكية واضحة في الفيديو
    - التصنيف الأكثر وضوحاً من: visual, sensory, motor, language

    كن دقيقاً وموضوعياً، ولا تضع تشخيصاً طبياً.
    """

    print("جاري تحليل الفيديو بالذكاء الاصطناعي...")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt, uploaded_file]
    )

    print("اكتمل التحليل!")
    return response.text