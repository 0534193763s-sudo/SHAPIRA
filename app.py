import os
from flask import Flask, request, Response
from google import genai

app = Flask(__name__)

# אתחול ג'ימני עם ה-SDK החדש
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route('/gemini-ivr', methods=['GET', 'POST'])
def gemini_ivr():
    # קבלת פרטי הקובץ מימות המשיח (בחינם)
    file_name = request.args.get('File')
    path = request.args.get('Path')
    
    # שלב א': המאזין רק נכנס לשלוחה -> מפעילים את הציפצוף וההקלטה החינמית
    if not file_name:
        recording_command = "type=record&say_record_menu=no&say_record_number=no&hangup_insert_file=no"
        return Response(recording_command, mimetype='text/plain')

    # שלב ב': ההקלטה הסתיימה -> שולחים את הקישור לג'ימיני שיקשיב בחינם
    try:
        # טוקן המערכת שלך מימות המשיח (הגדר ב-Render תחת YM_TOKEN)
        ym_token = os.environ.get("YM_TOKEN", "")
        file_url = f"https://ym-files.co{ym_token}&path={path}/{file_name}"
        
        # אנחנו מבקשים מג'ימיני להקשיב לקובץ ולענות בקצרות
        prompt = f"Listen to the audio file at this URL and answer briefly in Hebrew, suitable for phone text-to-speech: {file_url}"
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )
        
        # מחזירים את התשובה להקראה בחינם ומחזירים לתפריט הראשי (/) כדי שלא יהיה שקט
        ivr_output = f"id_list_message=t-{response.text}&go_to_folder=/"
        
    except Exception as e:
        ivr_output = "id_list_message=t-חלה שגיאה זמנית בעיבוד הנתונים. אנא נסו שוב.&go_to_folder=/"

    # חובה להחזיר כטקסט פשוט כדי שימות המשיח יבינו
    return Response(ivr_output, mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
