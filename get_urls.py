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

# --- 1から14ページまでループ処理 ---
for page_num in range(1, 15):  # 1から14ページ
    print(f"\n{'='*60}")
    print(f"🔄 ページ {page_num}/14 を処理中")
    print(f"{'='*60}")
    
    # --- LOVEGREEN 野菜一覧ページ ---
    if page_num == 1:
        url = "https://lovegreen.net/library/type/vegetables/page/1/"
    else:
        url = f"https://lovegreen.net/library/type/vegetables/page/{page_num}/"

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

        # vegetablesに関連するリンクを探す
        vegetable_links = []
        for a in a_with_href:
            href = a.get('href')
            if href and 'vegetables' in href:
                vegetable_links.append(a)

        print(f"vegetablesを含むリンク数: {len(vegetable_links)}")

        # 最初の10個のvegetableリンクを表示
        print("\n=== vegetablesリンクの最初の10個 ===")
        for i, link in enumerate(vegetable_links[:10]):
            href = link.get('href')
            text = link.get_text(strip=True)
            print(f"{i+1}. {text[:30]}... - {href}")

        # # HTMLダンプを保存（最初の3ページのみ）
        # if page_num <= 3:
        #     with open(f"vegetables_page_{page_num}_dump.html", "w", encoding="utf-8") as f:
        #         f.write(soup.prettify())
        #     print(f"\n💾 vegetables_page_{page_num}_dump.html を保存しました")

        # このページの植物データを抽出
        page_plant_data = []

        # vegetablesリンクから植物データを抽出
        for link in vegetable_links:
            href = link.get("href")
            text = link.get_text(strip=True)
            
            # 個別の植物ページのリンクかどうかを判定
            if href and text and len(text) > 0:
                # 完全なURLにする
                if href.startswith('/'):
                    full_url = "https://lovegreen.net" + href
                elif not href.startswith('http'):
                    full_url = "https://lovegreen.net/library/vegetables/" + href
                else:
                    full_url = href
                
                # 一覧ページ自体は除外
                if (not full_url.endswith('/vegetables/') and 
                    '/page/' not in full_url and
                    '/category/' not in full_url):
                    page_plant_data.append({"name": text, "url": full_url})
                    print(f"✓ {text} - {full_url}")

        # 元のセレクターも試す
        if len(cards) > 0:
            print(f"\n=== 元のセレクターでの抽出 ===")
            for card in cards:
                link = card.get("href")
                name_tag = card.find("span", class_="library-list__item__title")
                name = name_tag.get_text(strip=True) if name_tag else None

                if name and link:
                    full_url = link if link.startswith("http") else "https://lovegreen.net" + link
                    # 重複チェック
                    if not any(plant['url'] == full_url for plant in page_plant_data):
                        page_plant_data.append({"name": name, "url": full_url})
                        print(f"✓ {name} - {full_url}")

        # このページのデータを全体リストに追加（重複除去）
        new_count = 0
        existing_urls = {plant['url'] for plant in all_plant_data}
        
        for plant in page_plant_data:
            if plant['url'] not in existing_urls:
                all_plant_data.append(plant)
                new_count += 1
        
        print(f"\n📊 ページ {page_num}: {new_count}件の新しい野菜を追加 (累計: {len(all_plant_data)}件)")
        
    except Exception as e:
        print(f"❌ ページ {page_num} でエラーが発生: {e}")
        continue

# ドライバーを終了
driver.quit()

print(f"\n{'='*60}")
print("🎉 全ページの処理が完了しました")
print(f"{'='*60}")

# 重複を除去（最終チェック）
unique_plants = []
seen_urls = set()
for plant in all_plant_data:
    if plant['url'] not in seen_urls:
        unique_plants.append(plant)
        seen_urls.add(plant['url'])

plant_data = unique_plants

# --- CSVに保存 ---
if plant_data:
    with open("plant_urls.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "url"])
        writer.writeheader()
        writer.writerows(plant_data)

    print(f"\n✅ 完了：{len(plant_data)} 件の野菜データを plant_urls.csv に保存しました")
    
    # 最初の5件を表示
    print("\n📋 最初の5件:")
    for i, plant in enumerate(plant_data[:5]):
        print(f"  {i+1}. {plant['name']} - {plant['url']}")
        
    # 最後の5件を表示
    print("\n📋 最後の5件:")
    for i, plant in enumerate(plant_data[-5:]):
        print(f"  {len(plant_data)-4+i}. {plant['name']} - {plant['url']}")
else:
    print("\n❌ 植物データが見つかりませんでした")
    print("🔍 vegetables_page_*_dump.html を確認してください")
