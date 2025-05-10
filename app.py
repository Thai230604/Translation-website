from flask import Flask, render_template, request, jsonify
from utils.translator import Translator, TranslatorQuantized
import traceback

app = Flask(__name__)

# Khởi tạo translator
try:
    translator = TranslatorQuantized()
except Exception as e:
    print(f"Lỗi khi khởi tạo Translator: {str(e)}")
    raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        print(f"Received request: {data}")
        text = data.get('text', '').strip()
        direction = data.get('direction', 'en_to_vi')

        if not text:
            print("Lỗi: Văn bản rỗng")
            return jsonify({'translation': '', 'error': 'Văn bản rỗng'})

        # Tự động phát hiện ngôn ngữ
        if direction == 'auto':
            print("Phát hiện ngôn ngữ tự động...")
            if any(ord(char) > 127 for char in text):
                direction = 'vi_to_en'
            else:
                direction = 'en_to_vi'
            print(f"Hướng dịch: {direction}")

        print(f"Dịch: '{text}' ({direction})")
        translation = translator.translate(text, direction)
        print(f"Kết quả: '{translation}'")
        return jsonify({'translation': translation})

    except Exception as e:
        error_msg = f"Lỗi khi dịch: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'translation': '', 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)