import os
from flask import Flask, request
from google import genai

app = Flask(__name__)

# אתחול ג'ימני
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route('/gemini-ivr', methods=['GET', 'POST'])
def gemini_ivr():
    user_speech_text = request.args.get('ApiRecordedText') or request.args.get('ApiText')
    
    if not user_speech_text:
        return "read=t-לא שמעתי את שאלתך. אנא נסה שוב.=&voice_to_text=yes"

    try:
        prompt = f"השב בקצרות ובשפה פשוטה וברורה המתאימה להקראה טלפונית: {user_speech_text}"
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )
        return f"id_list_message=t-{response.text}."
    except Exception as e:
        return "id_list_message=t-חלה שגיאה זמנית. אנא נסה שוב מאוחר יותר."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
