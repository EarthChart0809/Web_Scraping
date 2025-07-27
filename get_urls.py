from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import csv

# --- Seleniumのオプション設定 ---
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=options)

# 全ページの植物データを格納するリスト
all_plant_data = []

# --- 植物カテゴリの設定 ---
plant_categories = [
    {
        "name": "野菜",
        "type": "vegetables",
        "url_base": "https://lovegreen.net/library/type/vegetables/",
        "max_pages": 14
    },
    {
        "name": "果樹",
        "type": "fruit-tree",
        "url_base": "https://lovegreen.net/library/type/fruit-tree/",
        "max_pages": 5
    },
    {
        "name": "花",
        "type": "flower",
        "url_base": "https://lovegreen.net/library/type/flower/",
        "max_pages": 62
    }
]

# --- 各カテゴリの処理 ---
for category in plant_categories:
  print(f"\n{'='*80}")
  print(f"🌱 {category['name']}の処理を開始")
  print(f"{'='*80}")

  # --- 各カテゴリのページループ処理 ---
  for page_num in range(1, category['max_pages'] + 1):
    print(f"\n{'='*60}")
    print(f"🔄 {category['name']} - ページ {page_num}/{category['max_pages']} を処理中")

    # --- LOVEGREEN 一覧ページ ---
    if page_num == 1:
      if category['type'] == 'vegetables':
        url = f"{category['url_base']}page/1"
      elif category['type'] == 'fruit-tree':
        url = f"{category['url_base']}page/1"
      else:  # flower
        url = category['url_base']
    else:
      url = f"{category['url_base']}page/{page_num}/"

    print(f"URL: {url}")

    try:
      driver.get(url)

      # JavaScriptの読み込みを待つ
      time.sleep(8)  # 待機時間を調整

      # ページ内容を取得
      html = driver.page_source
      soup = BeautifulSoup(html, "html.parser")

      # デバッグ情報を表示
      print("=== デバッグ情報 ===")
      print(f"ページタイトル: {soup.title.string if soup.title else 'なし'}")
      print(f"HTML全体のサイズ: {len(html)} 文字")

      # 元のセレクターを確認
      cards = soup.find_all("a", class_="library-list__item")
      print(f"library-list__item クラス: {len(cards)} 個")

      if len(cards) == 0:
        print("\n=== 代替セレクターを試しています ===")

        # 他の可能性のあるセレクターを試す
        alternative_selectors = [
            ("a", "card"),
            ("a", "item"),
            ("div", "card"),
            ("article", None),
            ("div", "item"),
            ("a", "library-item"),
            ("div", "library-list"),
            ("a", "plant-card"),
        ]

        for tag, class_name in alternative_selectors:
          if class_name:
            elements = soup.find_all(tag, class_=class_name)
            print(f"{tag}.{class_name}: {len(elements)} 個")
          else:
            elements = soup.find_all(tag)
            print(f"{tag}: {len(elements)} 個")

          if elements and len(elements) > 0:
            # 最初の要素を詳しく確認
            first_elem = elements[0]
            print(f"  最初の要素: {first_elem.name}")
            print(f"  クラス: {first_elem.get('class', [])}")
            print(f"  href: {first_elem.get('href', 'なし')}")

            # テキスト内容を確認
            text = first_elem.get_text(strip=True)
            if text:
              print(f"  テキスト: {text[:50]}...")

            # このセレクターでリンクを抽出してみる
            if first_elem.get('href'):
              cards = elements
              break

      # 全てのaタグを確認
      print(f"\n=== 全てのaタグを確認 ===")
      all_a_tags = soup.find_all("a")
      print(f"ページ内の全aタグ数: {len(all_a_tags)}")

      # hrefを持つaタグを確認
      a_with_href = [a for a in all_a_tags if a.get('href')]
      print(f"hrefを持つaタグ数: {len(a_with_href)}")

      # カテゴリに関連するリンクを探す
      category_links = []
      for a in a_with_href:
        href = a.get('href')
        if href and category['type'] in href:
          category_links.append(a)

      print(f"{category['type']}を含むリンク数: {len(category_links)}")

      # 最初の5個のカテゴリリンクを表示
      print(f"\n=== {category['type']}リンクの最初の5個 ===")
      for i, link in enumerate(category_links[:5]):
        href = link.get('href')
        text = link.get_text(strip=True)
        print(f"{i+1}. {text[:30]}... - {href}")

      # このページの植物データを抽出
      page_plant_data = []

      # カテゴリリンクから植物データを抽出
      for link in category_links:
        href = link.get("href")
        text = link.get_text(strip=True)

        # 個別の植物ページのリンクかどうかを判定
        if href and text and len(text) > 0:
          # 完全なURLにする
          if href.startswith('/'):
            full_url = "https://lovegreen.net" + href
          elif not href.startswith('http'):
            full_url = f"https://lovegreen.net/library/{category['type']}/" + href
          else:
            full_url = href

          # 除外するURLパターンを修正（より具体的に）
          exclude_patterns = [
              f'/type/{category["type"]}/',      # 一覧ページ自体（より具体的に）
              f'/type/{category["type"]}?',      # 一覧ページのパラメータ付き
              f'/type/{category["type"]}#',      # 一覧ページのアンカー付き
              '/page/',                          # ページネーション
              '/category/',                      # カテゴリページ
              'syllabary=',                      # 五十音順検索ページ
              f'?s&type={category["type"]}',     # 検索ページ
              '/search/',                        # 検索ページ
              '/tag/',                           # タグページ
              '/author/',                        # 作者ページ
              '/registration/',                  # 登録ページ
          ]

          # 除外パターンをチェック
          should_exclude = False
          for pattern in exclude_patterns:
            if pattern in full_url:
              should_exclude = True
              break

          # 五十音（1文字）のテキストも除外
          if len(text) == 1 and text in 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん':
            should_exclude = True

          # 個別植物ページの判定を追加
          # 個別植物ページのURLパターン: /library/カテゴリ/p数字/ または /library/カテゴリ/植物名/
          is_individual_page = False

          # pXXXXX形式のページID
          if '/p' in href and href.split('/p')[-1].rstrip('/').isdigit():
            is_individual_page = True

          # 植物名形式のURL（/library/カテゴリ/植物名/）
          url_parts = href.strip('/').split('/')
          if (len(url_parts) >= 3 and
              url_parts[0] == 'library' and
              url_parts[1] == category['type'] and
              len(url_parts[2]) > 1 and  # 植物名は1文字以上
                  not url_parts[2].startswith('p')):  # pXXXX形式でない
            is_individual_page = True

          # 個別植物ページで除外パターンに該当しないもののみを追加
          if is_individual_page and not should_exclude:
            page_plant_data.append(
                {"name": text, "url": full_url, "category": category['name']})
            print(f"✓ {text} - {full_url}")

      # 元のセレクターも試す
      if len(cards) > 0:
        print(f"\n=== 元のセレクターでの抽出 ===")
        for card in cards:
          link = card.get("href")
          name_tag = card.find("span", class_="library-list__item__title")
          name = name_tag.get_text(strip=True) if name_tag else None

          if name and link:
            full_url = link if link.startswith(
                "http") else "https://lovegreen.net" + link

            # 同じ除外ロジックを適用
            exclude_patterns = [
                f'/type/{category["type"]}/',
                f'/type/{category["type"]}?',
                f'/type/{category["type"]}#',
                '/page/',
                '/category/',
                'syllabary=',
                f'?s&type={category["type"]}',
                '/search/',
                '/tag/',
                '/author/',
                '/registration/',
            ]

            should_exclude = False
            for pattern in exclude_patterns:
              if pattern in full_url:
                should_exclude = True
                break

            # 五十音（1文字）のテキストも除外
            if len(name) == 1 and name in 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん':
              should_exclude = True

            # 個別植物ページの判定
            is_individual_page = False

            if '/p' in link and link.split('/p')[-1].rstrip('/').isdigit():
              is_individual_page = True

            url_parts = link.strip('/').split('/')
            if (len(url_parts) >= 3 and
                url_parts[0] == 'library' and
                url_parts[1] == category['type'] and
                len(url_parts[2]) > 1 and
                    not url_parts[2].startswith('p')):
              is_individual_page = True

            # 重複チェック & 除外チェック
            if (is_individual_page and not should_exclude and
                    not any(plant['url'] == full_url for plant in page_plant_data)):
              page_plant_data.append(
                  {"name": name, "url": full_url, "category": category['name']})
              print(f"✓ {name} - {full_url}")
            

      # このページのデータを全体リストに追加（重複除去）
      new_count = 0
      existing_urls = {plant['url'] for plant in all_plant_data}

      for plant in page_plant_data:
        if plant['url'] not in existing_urls:
          all_plant_data.append(plant)
          new_count += 1

      print(
          f"\n{category['name']} - ページ {page_num}: {new_count}件の新しい植物を追加 (累計: {len(all_plant_data)}件)")

    except Exception as e:
      print(f"❌ {category['name']} - ページ {page_num} でエラーが発生: {e}")
      continue

# ドライバーを終了
driver.quit()

print(f"\n{'='*80}")
print("全カテゴリの処理が完了しました")
print(f"{'='*80}")

# 重複を除去（最終チェック）
unique_plants = []
seen_urls = set()
for plant in all_plant_data:
  if plant['url'] not in seen_urls:
    unique_plants.append(plant)
    seen_urls.add(plant['url'])

plant_data = unique_plants

# カテゴリ別の統計情報を表示
print("\nカテゴリ別統計:")
category_stats = {}
for plant in plant_data:
  category = plant['category']
  category_stats[category] = category_stats.get(category, 0) + 1

for category, count in category_stats.items():
  print(f"  {category}: {count}件")

# --- 統合CSVに保存 ---
if plant_data:
  with open("all_plants_urls.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "url", "category"])
    writer.writeheader()
    writer.writerows(plant_data)

  print(f"\n✅ 完了：{len(plant_data)} 件の植物データを all_plants_urls.csv に保存しました")

  # 各カテゴリの最初の3件を表示
  print("\n各カテゴリの最初の3件:")
  for category_name in ["野菜", "果樹", "花"]:
    category_plants = [p for p in plant_data if p['category'] == category_name]
    if category_plants:
      print(f"\n  【{category_name}】")
      for i, plant in enumerate(category_plants[:3]):
        print(f"    {i+1}. {plant['name']} - {plant['url']}")
      if len(category_plants) > 3:
        print(f"    ... 他 {len(category_plants) - 3} 件")

  # 最後の5件を表示
  print(f"\n 最後の5件:")
  for i, plant in enumerate(plant_data[-5:]):
    print(
        f"  {len(plant_data)-4+i}. [{plant['category']}] {plant['name']} - {plant['url']}")

else:
  print("\n❌ 植物データが見つかりませんでした")

print(f"\n処理完了！合計 {len(plant_data)} 件の植物データを取得しました")
