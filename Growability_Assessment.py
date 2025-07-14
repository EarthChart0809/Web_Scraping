import json
import os
from typing import Dict, List, Optional

def score_grow_ease(texts):
  """育成難易度をスコア化する関数"""
  text = " ".join(texts).lower()  # 配列を1つの文字列にまとめて小文字に変換
  score = 0

  # 育てやすい表現（プラス評価）
  easy_keywords = [
      "育てやすい", "初心者", "簡単", "丈夫", "強い", "手間がかからない", "強健",
      "寒さに強い", "病気に強い", "水やり少ない", "日光があれば", "おすすめ", "失敗しにくい",
      "栽培しやすい", "管理が楽", "枯れにくい", "耐寒性", "耐暑性", "乾燥に強い",
      "放置", "手軽", "簡単に", "育てやすく", "初心者向け", "ビギナー",
      "プランター", "室内", "ベランダ", "手間いらず", "丈夫で", "強く",
      "育てやすい野菜", "作りやすい", "栽培が容易", "管理しやすい", "優れている",
      "日当たりを好み", "風通しの良い", "真冬でも", "ゆっくり", "生育します","放置","人気"
  ]

  # 育てにくい表現（マイナス評価）
  hard_keywords = [
      "難しい", "管理が必要", "剪定", "支柱", "病気に弱い", "繊細",
      "毎日水やり", "寒さに弱い", "暑さに弱い", "注意が必要", "手間がかかる",
      "発芽しにくい", "結実が難しい", "高温に弱い", "低温に弱い", "害虫に注意",
      "デリケート", "専門知識", "経験者向け", "温度管理", "湿度管理",
      "難易度が高い", "上級者", "コツが必要", "複雑", "手間", "困難",
      "乾燥すると生育が悪く", "こまめに行いましょう", "加湿に注意", "病害虫が発生","発芽しにくい",
      "失敗しやすい", "栽培が難しい", "管理が大変",  "育てにくい","種","アブラムシ",
      "うどんこ病","モザイク病","根腐れ","頻繁に水やり","ヨトウムシ","木酢液","害虫対策",
      "食味が落ち"
  ]

  # デバッグ用: マッチしたキーワードを確認
  matched_easy = []
  matched_hard = []

  for kw in easy_keywords:
    if kw in text:
      score += 1
      matched_easy.append(kw)

  for kw in hard_keywords:
    if kw in text:
      score -= 1
      matched_hard.append(kw)

  # デバッグ情報を出力（マッチしたキーワードがある場合のみ）
  if matched_easy or matched_hard:
    print(f"  マッチしたキーワード - 簡単: {matched_easy[:3]}, 難しい: {matched_hard[:3]}")

  return max(0, min(score, 5))  # スコアは0〜5の範囲に制限

def load_plant_data(json_file_path: str) -> Optional[Dict]:
  """JSONファイルから植物データを読み込む"""
  try:
    if not os.path.exists(json_file_path):
      print(f"❌ ファイルが見つかりません: {json_file_path}")
      return None

    with open(json_file_path, 'r', encoding='utf-8') as f:
      data = json.load(f)
      print(f"✅ JSONファイルを読み込みました: {json_file_path}")
      return data
  except json.JSONDecodeError as e:
    print(f"❌ JSONファイルの形式が正しくありません: {e}")
    return None
  except Exception as e:
    print(f"❌ ファイル読み込みエラー: {e}")
    return None

def assess_plant_growability(plant_data: Dict, plant_name: str) -> Dict:
  """単一の植物の育成難易度を評価する"""

  if plant_name not in plant_data:
    return {
        "植物名": plant_name,
        "評価": "データなし",
        "スコア": 0,
        "理由": "植物データが見つかりません"
    }

  plant_info = plant_data[plant_name]

  # テキストデータを収集
  texts = []

  # データがリスト形式の場合
  if isinstance(plant_info, list):
    # リスト内の全ての文字列を結合
    for item in plant_info:
      if isinstance(item, str) and len(item) > 0:
        texts.append(item)

  # データが辞書形式の場合（従来の形式）
  elif isinstance(plant_info, dict):
    if "基本情報" in plant_info and plant_info["基本情報"]:
      texts.append(plant_info["基本情報"])

    if "栽培方法" in plant_info and plant_info["栽培方法"]:
      if isinstance(plant_info["栽培方法"], list):
        texts.extend(plant_info["栽培方法"])
      else:
        texts.append(str(plant_info["栽培方法"]))

    if "特徴" in plant_info and plant_info["特徴"]:
      if isinstance(plant_info["特徴"], list):
        texts.extend(plant_info["特徴"])
      else:
        texts.append(str(plant_info["特徴"]))

    if "その他" in plant_info and plant_info["その他"]:
      if isinstance(plant_info["その他"], list):
        texts.extend(plant_info["その他"])
      else:
        texts.append(str(plant_info["その他"]))

  # デバッグ用: テキストの内容を確認
  print(f"\n🔍 {plant_name} の分析:")
  print(f"  テキスト数: {len(texts)}")
  if texts:
    combined_text = " ".join(texts)
    print(f"  テキスト例: {combined_text[:100]}...")

  # スコア計算
  score = score_grow_ease(texts)

  # 評価レベル決定
  if score >= 4:
    level = "とても育てやすい"
  elif score >= 3:
    level = "育てやすい"
  elif score >= 2:
    level = "普通"
  elif score >= 1:
    level = "やや難しい"
  else:
    level = "難しい"

  return {
      "植物名": plant_name,
      "評価": level,
      "スコア": score,
      "理由": f"分析したテキスト: {len(texts)}件, スコア: {score}"
  }

def assess_all_plants(plant_data: Dict) -> List[Dict]:
  """すべての植物の育成難易度を評価する"""
  results = []

  print(f"🔄 {len(plant_data)}件の植物を評価中...")

  for i, plant_name in enumerate(plant_data.keys()):
    print(f"\n📊 評価中 ({i+1}/{len(plant_data)}): {plant_name}")
    result = assess_plant_growability(plant_data, plant_name)
    results.append(result)

    # 最初の3件だけ詳細を表示
    if i >= 2:
      print("\n  (以降の詳細表示を省略...)")
      break

  # 残りの植物を評価（詳細表示なし）
  for plant_name in list(plant_data.keys())[3:]:
    result = assess_plant_growability(plant_data, plant_name)
    results.append(result)

  # スコア順でソート
  results.sort(key=lambda x: x["スコア"], reverse=True)

  return results

def debug_plant_data(plant_data: Dict, limit: int = 3):
  """植物データの内容を確認する"""
  print(f"\n🔍 植物データの内容確認 (最初の{limit}件):")
  print("=" * 60)

  for i, (plant_name, plant_info) in enumerate(plant_data.items()):
    if i >= limit:
      break

    print(f"\n植物名: {plant_name}")
    print(f"データ型: {type(plant_info)}")

    if isinstance(plant_info, list):
      print(f"リスト要素数: {len(plant_info)}")
      if plant_info:
        print(f"  最初の要素: {plant_info[0][:50]}...")
        print(f"  最後の要素: {plant_info[-1][:50]}...")
    elif isinstance(plant_info, dict):
      print(f"フィールド: {list(plant_info.keys())}")
      for field, value in plant_info.items():
        if isinstance(value, list):
          print(f"  {field}: リスト({len(value)}件)")
          if value:
            print(f"    例: {value[0][:50]}...")
        elif isinstance(value, str):
          print(f"  {field}: 文字列({len(value)}文字)")
          if value:
            print(f"    例: {value[:50]}...")
        else:
          print(f"  {field}: {type(value)} - {value}")
    else:
      print(f"内容: {str(plant_info)[:100]}...")

    print("-" * 40)

def save_assessment_results(results: List[Dict], output_file: str):
  """評価結果をJSONファイルに保存"""
  try:
    with open(output_file, 'w', encoding='utf-8') as f:
      json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ 評価結果を保存しました: {output_file}")
  except Exception as e:
    print(f"❌ 結果保存エラー: {e}")

def print_assessment_summary(results: List[Dict]):
  """評価結果のサマリーを表示"""
  print(f"\n{'='*60}")
  print("🌱 植物育成難易度評価結果")
  print(f"{'='*60}")

  total_plants = len(results)
  print(f"📊 評価対象植物数: {total_plants}件")

  # 評価レベル別の集計
  level_counts = {}
  for result in results:
    level = result["評価"]
    level_counts[level] = level_counts.get(level, 0) + 1

  print(f"\n📈 評価レベル別集計:")
  for level, count in level_counts.items():
    percentage = (count / total_plants * 100) if total_plants > 0 else 0
    print(f"  {level}: {count}件 ({percentage:.1f}%)")

  # 上位5件を表示
  print(f"\n🏆 育てやすい植物 TOP5:")
  for i, result in enumerate(results[:5]):
    print(f"  {i+1}. {result['植物名']} - {result['評価']} (スコア: {result['スコア']})")

  # 下位5件を表示
  print(f"\n⚠️ 育てにくい植物 ワースト5:")
  for i, result in enumerate(results[-5:]):
    rank = total_plants - len(results[-5:]) + i + 1
    print(f"  {rank}. {result['植物名']} - {result['評価']} (スコア: {result['スコア']})")

def main():
  """メイン処理"""
  print("🌱 植物育成難易度評価システム")
  print("=" * 50)

  # JSONファイル名を指定
  json_file_path = input("JSONファイルのパスを入力してください: ").strip()

  if not json_file_path:
    json_file_path = "vegetable_data_structured.json"  # デフォルト値
    print(f"デフォルトファイルを使用します: {json_file_path}")

  # データ読み込み
  plant_data = load_plant_data(json_file_path)
  if not plant_data:
    return

  print(f"📋 読み込んだ植物数: {len(plant_data)}件")

  # デバッグ: データ内容を確認
  debug_plant_data(plant_data)

  # 評価実行
  print("\n🔄 評価を実行中...")
  results = assess_all_plants(plant_data)

  # 結果表示
  print_assessment_summary(results)

  # 結果保存
  output_file = "plant_growability_assessment.json"
  save_assessment_results(results, output_file)

  # 詳細結果をテキストファイルに保存
  with open("plant_growability_report.txt", "w", encoding="utf-8") as f:
    f.write("植物育成難易度評価レポート\n")
    f.write("=" * 50 + "\n\n")

    for result in results:
      f.write(f"植物名: {result['植物名']}\n")
      f.write(f"評価: {result['評価']}\n")
      f.write(f"スコア: {result['スコア']}\n")
      f.write(f"理由: {result['理由']}\n")
      f.write("-" * 30 + "\n")

  print("📄 詳細レポートを保存しました: plant_growability_report.txt")

if __name__ == "__main__":
  main()
