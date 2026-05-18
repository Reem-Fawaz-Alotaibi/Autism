import time
from google import genai

client = genai.Client(
    api_key="AIzaSyB1CviMAzNhzRCe3zg3xgtKZ6s8oC_lOlU"
)

def analyze_video(video_file_path):
    print("جاري رفع الفيديو إلى سيرفرات Gemini...")
    uploaded_file = client.files.upload(file=video_file_path)
    print(f"تم الرفع بنجاح. المعرف السحابي للملف هو: {uploaded_file.name}")

    print("بدء مرحلة معالجة الفيديو وسنستخدم الـ time للانتظار...")
    
    while True:
        file_info = client.files.get(name=uploaded_file.name)
        print(f"حالة الفيديو الحالية في السيرفر: {file_info.state.name}")
        
        if file_info.state.name == "ACTIVE":
            print("رائع! الفيديو أصبح جاهزاً تماماً للتحليل الآن.")
            break
        elif file_info.state.name == "FAILED":
            raise Exception("فشلت معالجة الفيديو داخل سيرفرات جوجل.")
            
        time.sleep(7)

    prompt = """
    Analyze this video and describe what you observe.
    Focus on: main activities, people or movement, environment, important visual details.
    Give a clear short summary.
    """

    print("جاري إرسال الفيديو والـ prompt إلى الموديل الذكي...")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt, uploaded_file]
    )

    print("تمت عملية التحليل بنجاح واكتمل التقرير!")
    return response.text