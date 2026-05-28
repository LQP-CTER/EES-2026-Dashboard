"""
Script kiểm tra model nào của Groq đang hoạt động thực tế với API keys của dự án.
Chạy: python scratch/check_groq_models.py
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from groq import Groq
import json

# Đọc key từ .streamlit/secrets.toml
try:
    import toml
    secrets_path = os.path.join(os.path.dirname(__file__), '..', '.streamlit', 'secrets.toml')
    secrets = toml.load(secrets_path)
    keys = [v for k, v in secrets.items() if 'groq' in k.lower() and v != 'dien-api-key-cua-ban-vao-day']
except Exception as e:
    print(f"Không đọc được secrets.toml: {e}")
    keys = [os.environ.get("GROQ_API_KEY", "")]
    keys = [k for k in keys if k]

if not keys:
    print("Không có API key nào!")
    sys.exit(1)

print(f"Tìm thấy {len(keys)} key. Dùng key đầu tiên để query models...")

client = Groq(api_key=keys[0])

# Lấy danh sách models hiện hành
try:
    models_resp = client.models.list()
    active_ids = sorted([m.id for m in models_resp.data])
    print(f"\nCác model đang hoạt động ({len(active_ids)} models):")
    for m in active_ids:
        print(f"  - {m}")
except Exception as e:
    print(f"Lỗi khi query models: {e}")
    sys.exit(1)

# Thử generate nhanh với từng candidate model
CANDIDATES = [
    "llama-3.3-70b-versatile",
    "qwen-2.5-32b",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
    "llama3-8b-8192",
    "llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "compound-beta",
    "compound-beta-mini",
]

print("\nKiểm tra model nào hoạt động:")
working = []
for model in CANDIDATES:
    try:
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": "Reply with just: OK"}],
            model=model,
            max_tokens=5,
            stream=False
        )
        print(f"  [OK] {model}")
        working.append(model)
    except Exception as e:
        err = str(e)[:80]
        print(f"  [FAIL] {model}: {err}")

print(f"\nCopy danh sách này vào GROQ_MODELS:")
print("GROQ_MODELS = [")
for m in working:
    print(f'    "{m}",')
print("]")
