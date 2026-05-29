import os
import json
import base64
import requests
import time
from pathlib import Path

# ============== 設定ここを書き換えて ==============
ENDPOINT_ID = "your-endpoint-id-here"
API_KEY = "your-runpod-api-key-here"
WORKFLOW_PATH = "api-workflow.json"

INPUT_DIR = "input_images"
OUTPUT_DIR = "output_videos"
POS_PROMPT_FILE = "queue_positive-prompt.txt"
NEG_PROMPT_FILE = "queue_negative-prompt.txt"
# ================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# プロンプトを読み込み
with open(POS_PROMPT_FILE, "r", encoding="utf-8") as f:
    positive_prompt = f.read().replace("\n", " ").replace("\r", " ").strip()

with open(NEG_PROMPT_FILE, "r", encoding="utf-8") as f:
    negative_prompt = f.read().replace("\n", " ").replace("\r", " ").strip()

# ワークフロー読み込み
with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
    workflow = json.load(f)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print("=== RunPod Serverless Wan2.2 動画生成スタート ===")
print(f"Positive Prompt: {positive_prompt[:100]}..." if len(positive_prompt) > 100 else f"Positive Prompt: {positive_prompt}")
print(f"Negative Prompt: {negative_prompt[:100]}..." if len(negative_prompt) > 100 else f"Negative Prompt: {negative_prompt}")

for image_file in sorted(Path(INPUT_DIR).glob("*.*")):
    if image_file.suffix.lower() not in [".png", ".jpg", ".jpeg", ".webp"]:
        continue

    print(f"\n処理中: {image_file.name}")

    try:
        input_image_base64 = image_to_base64(image_file)

        payload = {
            "input": {
                "workflow": workflow,
                "input_image": input_image_base64,
                "prompt": positive_prompt,
                "negative_prompt": negative_prompt,
                # 必要ならここに seed, steps, cfg などのパラメータも追加可能
            }
        }

        response = requests.post(
            f"https://api.runpod.ai/v2/{ENDPOINT_ID}/run",
            json=payload,
            headers=headers
        )

        if response.status_code != 200:
            print(f"リクエストエラー: {response.text}")
            continue

        job_id = response.json().get("id")
        print(f"  → Job ID: {job_id}")

        # 結果ポーリング
        while True:
            status_res = requests.get(
                f"https://api.runpod.ai/v2/{ENDPOINT_ID}/status/{job_id}",
                headers=headers
            )
            status = status_res.json()

            if status.get("status") == "COMPLETED":
                print(f"  ✅ 完了: {image_file.name}")
                # ここに動画ダウンロード処理を後で追加してもいいよ
                break
            elif status.get("status") == "FAILED":
                print(f"  ❌ 失敗: {status.get('error')}")
                break

            time.sleep(6)

    except Exception as e:
        print(f"エラー発生: {e}")

print("\n=== 全部完了しました ===")