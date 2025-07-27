from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
import csv

# Seleniumのオプション設定（画面表示なし）
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# User-Agentを追加（重要）
options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

# ドライバー起動
driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=options)

# --- CSVから読み込み ---
plant_pages = []
try:
  with open("all_plants_urls.csv", newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
      plant_pages.append(row)
  print(f" CSVファイルから {len(plant_pages)} 件のデータを読み込みました")
except FileNotFoundError:
  print("❌ all_plants_urls.csv ファイルが見つかりません")
  driver.quit()
  exit()

# スクレイピング結果を保存する辞書
scraped_data = {}

# 各植物のページを順番にスクレイピング
for i, row in enumerate(plant_pages):
  # CSVのカラム名を確認して適切にアクセス
  if 'plant_name' in row and 'url' in row:
    plant_name = row['plant_name']
    url = row['url']
  elif 'name' in row and 'url' in row:
    plant_name = row['name']
    url = row['url']
  else:
    # CSVのカラム名が不明な場合、最初の2つのカラムを使用
    keys = list(row.keys())
    if len(keys) >= 2:
      plant_name = row[keys[0]]
      url = row[keys[1]]
    else:
      print(f"❌ 行 {i+1}: CSVの形式が正しくありません")
      continue

  print(f"\n{'='*50}")
  print(f"🌱 {plant_name} のスクレイピング開始 ({i+1}/{len(plant_pages)})")
  print(f"URL: {url}")
  print(f"{'='*50}")

  try:
    # ページにアクセス
    driver.get(url)

    # JavaScript読み込みの待機
    time.sleep(5)

    # ページのHTMLを取得
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # デバッグ: 基本情報を確認
    print(f"ページタイトル: {soup.title.string if soup.title else 'なし'}")
    print(f"HTML全体のサイズ: {len(html)} 文字")

    # セレクターを確認
    body = soup.find_all("div", class_="article__body")
    print(f"article__body クラスの要素数: {len(body)}")

    if len(body) == 0:
      print("代替セレクターを試しています...")
      # 他の可能性のあるセレクターを試す
      alternative_selectors = [
          ("div", "single__section__body"),
          ("div", "entry-content"),
          ("div", "post-content"),
          ("div", "content"),
          ("article", None),
          ("main", None),
      ]

      for tag, class_name in alternative_selectors:
        if class_name:
          elements = soup.find_all(tag, class_=class_name)
        else:
          elements = soup.find_all(tag)

        if elements:
          for elem in elements:
            paragraphs = elem.find_all("p")
            if paragraphs:
              print(
                  f"✅ {tag}.{class_name if class_name else 'なし'}: {len(paragraphs)} 個の段落を発見")
              body = elements  # 見つかったら使用
              break
          if body:
            break

    # テキスト抽出
    plant_content = []
    text_found = False

    for section in body:
      for elem in section.find_all(["h2", "h3", "p"]):
        text = elem.get_text().strip()
        if text:
          plant_content.append(text)
          text_found = True

    if text_found:
      print(f"✅ {plant_name}: {len(plant_content)} 個のテキスト要素を取得")
      scraped_data[plant_name] = plant_content

    else:
      print(f"❌ {plant_name}: テキストが見つかりませんでした")
      scraped_data[plant_name] = []

      # 全てのpタグを確認
      all_p_tags = soup.find_all("p")
      if all_p_tags:
        print(f"ページ内の全pタグ数: {len(all_p_tags)}")
        for j, p in enumerate(all_p_tags[:3]):
          text = p.get_text().strip()
          if text:
            print(f"p{j+1}: {text[:100]}...")

  except Exception as e:
    print(f"❌ {plant_name} のスクレイピング中にエラーが発生: {str(e)}")
    scraped_data[plant_name] = []

  # 次のページへのアクセス間隔を設ける
  time.sleep(2)

# ドライバー終了
driver.quit()

# 結果をまとめて表示
print(f"\n{'='*60}")
print("スクレイピング結果まとめ")
print(f"{'='*60}")

for plant_name, content in scraped_data.items():
  print(f"\n🌱 {plant_name}:")
  print(f"   取得したテキスト数: {len(content)}")
  if content:
    print(f"   最初のテキスト: {content[0][:100]}...")
  else:
    print("   ❌ テキストが取得できませんでした")

# JSONとして保存
with open("all_plants_data.json", "w", encoding="utf-8") as f:
  json.dump(scraped_data, f, ensure_ascii=False, indent=2)

print("\n✅ 完了：all_plant_data.json に保存されました")
