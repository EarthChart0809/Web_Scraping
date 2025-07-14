from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import json
from Growability_Assessment import load_plant_data, assess_all_plants, save_assessment_results

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
RESULT_FILE = "plant_growability_assessment.json"

# アップロード用ディレクトリを作成
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['json_file']
    if file and file.filename.endswith('.json'):
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # データ読み込みと評価
        plant_data = load_plant_data(file_path)
        if plant_data is None:
            return "❌ JSONの読み込みに失敗しました"

        results = assess_all_plants(plant_data)
        save_assessment_results(results, RESULT_FILE)

        return redirect(url_for('result'))

    return "❌ 有効なJSONファイルをアップロードしてください"

@app.route('/result')
def result():
    with open(RESULT_FILE, encoding='utf-8') as f:
        results = json.load(f)
    return render_template('result.html', results=results)

@app.route('/download')
def download():
    return send_file(RESULT_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
