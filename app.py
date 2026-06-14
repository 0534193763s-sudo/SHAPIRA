import os
from flask import Flask, request, Response
import google.generativeai as genai

app = Flask(__name__)

# אתחול תקין של ג'ימני לפי הספרייה הרשמית
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# נתיב ראשי - ככה לא צריך להסתבך עם סיומות בקישור של ימות המשיח
@app.route('/', methods=['GET', 'POST'])
def gemini_ivr():
    # בדיקה האם ימות המשיח כבר שלחו קובץ שהוקלט
    file_name = request.args.get('File')
    path = request.args.get('Path')
    
    # שלב א': המאזין רק נכנס (אין עדיין קובץ) -> מפעילים ציפצוף והקלטה בחינם!
    if not file_name:
        recording_command = "type=record&say_record_menu=no&say_record_number=no&hangup_insert_file=no"
        return Response(recording_command, mimetype='text/plain')

    # שלב ב': יש קובץ מוקלט -> שולחים לג'ימיני ומקבלים תשובה
    try:
        # טוקן המערכת שלך (חובה להגדיר ב-Render תחת השם YM_TOKEN)
        ym_token = os.environ.get("YM_TOKEN", "")
        file_url = f"https://ym-files.co{ym_token}&path={path}/{file_name}"
        
        # שימוש במודל החינמי והיציב ביותר שמתאים לקבצי שמע
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"Listen to the audio file at this URL and answer briefly in Hebrew, suitable for phone text-to-speech: {file_url}"
        response = model.generate_content(prompt)
        
        gemini_text = response.text.strip()
        
        # מחזירים את התשובה להקראה ומחזירים לתפריט הראשי (/) כדי שלא יהיה שקט
        ivr_output = f"id_list_message=t-{gemini_text}&go_to_folder=/"
        
    except Exception as e:
        # במקרה של שגיאה, המערכת לא תשתוק אלא תגיד שמשהו השתבש
        ivr_output = "id_list_message=t-חלה שגיאה זמנית בעיבוד הנתונים. אנא נסו שוב.&go_to_folder=/"

    # חובה להחזיר text/plain כדי שימות המשיח יבינו ולא יתקעו בשקט
    return Response(ivr_output, mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
