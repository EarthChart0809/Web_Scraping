import json
import os
from typing import Dict, List, Optional

def score_grow_ease(texts):
  """育成難易度をスコア化する関数（重み付きキーワード）"""
  text = " ".join(texts).lower()  # 配列を1つの文字列にまとめて小文字に変換
  score = 0

  # 育てやすい表現（プラス評価）- 重み付き
  easy_keywords = {
      # 高重要度 (重み: 3.0)
      "育てやすい": 3.0,"初心者": 3.0,"簡単": 3.0,"手間がかからない": 3.0,"失敗しにくい": 3.0,
      "栽培しやすい": 3.0,"管理が楽": 3.0,"初心者向け": 3.0,"手間いらず": 3.0,"作りやすい": 3.0,
      "栽培が容易": 3.0,"管理しやすい": 3.0,

      # 中重要度 (重み: 2.0)
      "丈夫": 2.0,"強い": 2.0,"強健": 2.0,"枯れにくい": 2.0,"耐寒性": 2.0,"耐暑性": 2.0,
      "寒さに強い": 2.0,"病気に強い": 2.0,"乾燥に強い": 2.0,"手軽": 2.0,"簡単に": 2.0,
      "ビギナー": 2.0,"丈夫で": 2.0,"強く": 2.0,"優れている": 2.0,

      # 低重要度 (重み: 1.0)
      "水やり少ない": 1.0,"日光があれば": 1.0,"おすすめ": 1.0,"放置": 1.0,"育てやすく": 1.0,
      "プランター": 1.0,"室内": 1.0,"ベランダ": 1.0,"育てやすい野菜": 1.0,"日当たりを好み": 1.0,
      "風通しの良い": 1.0,"真冬でも": 1.0,"ゆっくり": 1.0,"生育します": 1.0,"人気": 1.0,
  }

  # 育てにくい表現（マイナス評価）- 重み付き
  hard_keywords = {
      # 高重要度 (重み: -3.0)
      "難しい": -3.0,"繊細": -3.0,"デリケート": -3.0,"専門知識": -3.0,"経験者向け": -3.0,
      "難易度が高い": -3.0,"上級者": -3.0,"複雑": -3.0,"困難": -3.0,"失敗しやすい": -3.0,
      "栽培が難しい": -3.0,"管理が大変": -3.0,"育てにくい": -3.0,

      # 中重要度 (重み: -2.0)
      "管理が必要": -2.0,"病気に弱い": -2.0,"寒さに弱い": -2.0,"暑さに弱い": -2.0,"注意が必要": -2.0,
      "手間がかかる": -2.0,"発芽しにくい": -2.0,"結実が難しい": -2.0,"高温に弱い": -2.0,
      "低温に弱い": -2.0,"害虫に注意": -2.0,"温度管理": -2.0,"湿度管理": -2.0,"コツが必要": -2.0,
      "手間": -2.0,"乾燥すると生育が悪く": -2.0,"こまめに行いましょう": -2.0,

      # 低重要度 (重み: -1.0)
      "剪定": -1.0,"支柱": -1.0,"毎日水やり": -1.0,"加湿に注意": -1.0,"病害虫が発生": -1.0,
      # "種": -1.0,
      "アブラムシ": -1.0,"うどんこ病": -1.0,"モザイク病": -1.0,"根腐れ": -1.0,
      "頻繁に水やり": -1.0,"ヨトウムシ": -1.0,"木酢液": -1.0,"害虫対策": -1.0,"食味が落ち": -1.0,
  }

  # デバッグ用: マッチしたキーワードを確認
  matched_easy = []
  matched_hard = []

  # プラス評価キーワードのチェック
  for keyword, weight in easy_keywords.items():
    if keyword in text:
      score += weight
      matched_easy.append((keyword, weight))

  # マイナス評価キーワードのチェック
  for keyword, weight in hard_keywords.items():
    if keyword in text:
      score += weight  # weightは既に負の値
      matched_hard.append((keyword, weight))

  # デバッグ情報を出力（マッチしたキーワードがある場合のみ）
  if matched_easy or matched_hard:
    print(f"  マッチしたキーワード:")
    if matched_easy:
      easy_str = ", ".join([f"{kw}({w})" for kw, w in matched_easy[:3]])
      print(f"    簡単: {easy_str}")
    if matched_hard:
      hard_str = ", ".join([f"{kw}({w})" for kw, w in matched_hard[:3]])
      print(f"    難しい: {hard_str}")
    print(f"    合計スコア: {score:.1f}")

  return max(0, min(score, 10))  # スコアは0〜10の範囲に拡大

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

  # 評価レベル決定（10点満点に対応）
  if score >= 8:
    level = "とても育てやすい"
  elif score >= 6:
    level = "育てやすい"
  elif score >= 4:
    level = "普通"
  elif score >= 2:
    level = "やや難しい"
  else:
    level = "難しい"

  return {
      "植物名": plant_name,
      "評価": level,
      "スコア": round(score, 1),
      "理由": f"分析したテキスト: {len(texts)}件, 重み付きスコア: {score:.1f}"
  }

def assess_all_plants(plant_data: Dict) -> List[Dict]:
  """すべての植物の育成難易度を評価する"""
  results = []

  print(f"🔄 {len(plant_data)}件の植物を評価中...")

  for i, plant_name in enumerate(plant_data.keys()):
    print(f"\n評価中 ({i+1}/{len(plant_data)}): {plant_name}")
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

def get_keyword_weights_summary():
  """キーワード重みの設定を表示"""
  print("\nキーワード重み設定:")
  print("=" * 50)

  print("【育てやすさキーワード】")
  print("  高重要度 (重み: 3.0): 育てやすい, 初心者, 簡単, 手間がかからない等")
  print("  中重要度 (重み: 2.0): 丈夫, 強い, 耐寒性, 病気に強い等")
  print("  低重要度 (重み: 1.0): おすすめ, 人気, プランター, 室内等")

  print("\n【育てにくさキーワード】")
  print("  高重要度 (重み: -3.0): 難しい, 繊細, 専門知識, 経験者向け等")
  print("  中重要度 (重み: -2.0): 管理が必要, 病気に弱い, 注意が必要等")
  print("  低重要度 (重み: -1.0): 剪定, 支柱, アブラムシ, 害虫対策等")

  print("\nスコア範囲: 0〜10点 (10点が最も育てやすい)")

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
  print("🌱 植物育成難易度評価結果 (重み付きキーワード版)")
  print(f"{'='*60}")

  total_plants = len(results)
  print(f"評価対象植物数: {total_plants}件")

  # スコア統計
  scores = [result["スコア"] for result in results]
  avg_score = sum(scores) / len(scores) if scores else 0
  max_score = max(scores) if scores else 0
  min_score = min(scores) if scores else 0

  print(f"スコア統計:")
  print(f"  平均スコア: {avg_score:.1f}点")
  print(f"  最高スコア: {max_score:.1f}点")
  print(f"  最低スコア: {min_score:.1f}点")

  # 評価レベル別の集計
  level_counts = {}
  for result in results:
    level = result["評価"]
    level_counts[level] = level_counts.get(level, 0) + 1

  print(f"\n評価レベル別集計:")
  for level, count in level_counts.items():
    percentage = (count / total_plants * 100) if total_plants > 0 else 0
    print(f"  {level}: {count}件 ({percentage:.1f}%)")

  # 上位10件を表示
  print(f"\n🏆 育てやすい植物 TOP10:")
  for i, result in enumerate(results[:10]):
    print(f"  {i+1:2d}. {result['植物名']} - {result['評価']} ({result['スコア']}点)")

  # 下位5件を表示
  print(f"\n⚠️ 育てにくい植物 ワースト5:")
  for i, result in enumerate(results[-5:]):
    rank = total_plants - len(results[-5:]) + i + 1
    print(f"  {rank:2d}. {result['植物名']} - {result['評価']} ({result['スコア']}点)")

def main():
  """メイン処理"""
  print("🌱 植物育成難易度評価システム (重み付きキーワード版)")
  print("=" * 60)

  # キーワード重み設定を表示
  get_keyword_weights_summary()

  # JSONファイル名を指定
  json_file_path = input("\nJSONファイルのパスを入力してください: ").strip()

  if not json_file_path:
    json_file_path = "vegetable_data_structured.json"  # デフォルト値
    print(f"デフォルトファイルを使用します: {json_file_path}")

  # データ読み込み
  plant_data = load_plant_data(json_file_path)
  if not plant_data:
    return

  print(f"読み込んだ植物数: {len(plant_data)}件")

  # デバッグ: データ内容を確認
  debug_plant_data(plant_data)

  # 評価実行
  print("\n評価を実行中...")
  results = assess_all_plants(plant_data)

  # 結果表示
  print_assessment_summary(results)

  # 結果保存
  output_file = "plant_growability_assessment_weighted.json"
  save_assessment_results(results, output_file)

  # 詳細結果をテキストファイルに保存
  with open("plant_growability_report_weighted.txt", "w", encoding="utf-8") as f:
    f.write("植物育成難易度評価レポート (重み付きキーワード版)\n")
    f.write("=" * 60 + "\n\n")

    for result in results:
      f.write(f"植物名: {result['植物名']}\n")
      f.write(f"評価: {result['評価']}\n")
      f.write(f"スコア: {result['スコア']}点\n")
      f.write(f"理由: {result['理由']}\n")
      f.write("-" * 30 + "\n")

  print("詳細レポートを保存しました: plant_growability_report_weighted.txt")

if __name__ == "__main__":
  main()
