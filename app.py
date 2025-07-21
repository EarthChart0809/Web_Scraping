from flask import Flask, render_template, request
from Growability_Assessment import assess_all_plants, load_plant_data

app = Flask(__name__)

# 既に保存されているJSONファイルのパス
JSON_PATH = "data/plant_data.json"

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        try:
            # JSONファイルを読み込んで評価
            plant_data = load_plant_data(JSON_PATH)
            results = assess_all_plants(plant_data)
        except Exception as e:
            results = [{"植物名": "読み込みエラー", "評価": str(e), "スコア": 0}]
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)  # サーバー外部からアクセス可能にする場合
