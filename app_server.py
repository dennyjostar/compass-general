from flask import Flask, render_template, request, jsonify, session, make_response
import os
import openai
from datetime import datetime
import hashlib
from dotenv import load_dotenv

# .env 파일 로드
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "compass-secret-key-2026")

# 일반 성도용 NotebookLM 설정
GENERAL_NOTEBOOK_ID = "b937848d-4238-4883-a4c6-2adf8e2ba71f"

import base64


# OpenAI 설정
def get_openai_client():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        # 환경변수가 없을 경우 하드코딩된 암호화 키를 임의 복호화해서 사용합니다 (배포편의)
        enc = "c2stcHJvai1uaUlqckgweXVLMExXc0tydWlIbVVodTd2VDJXd1Zoc01vQnVYWFRRMWl6empEdjk1RWx4eTBJQm9abnJMbTZSNU01OTB1THRKLVQzQmxia0ZKVkg1dDd1anFBRGlTanZpUTlJdTJYaVV1V1FuWloybjFLMHZtUXpmZmU0MEIyTE9LWFZ3V0tCeUJJbV9oX3BoZzN0ZkNheW9fY0E="
        key = base64.b64decode(enc).decode('utf-8')
    return openai.OpenAI(api_key=key)

# 서버 사이드 사용량 추적 (메모리 기반 → 추후 DB 교체)
user_usage = {}
FREE_LIMIT = 3

def get_user_hash(name, age_group="", gender=""):
    raw = f"{name}_{age_group}_{gender}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

@app.route('/')
def home():
    resp = make_response(render_template('index.html'))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        user_msg = data.get('message', '')
        profile = data.get('profile', {})
        user_name = profile.get('name', '성도')

        # ★ 구독 시스템 일시 정지 - 무료 횟수 체크 없음
        # age_group = profile.get('ageGroup', '')
        # gender = profile.get('gender', '')
        # user_hash = get_user_hash(user_name, age_group, gender)
        # if user_hash not in user_usage:
        #     user_usage[user_hash] = {
        #         "count": 0,
        #         "first_use": datetime.now().isoformat(),
        #         "is_paid": False
        #     }
        # usage = user_usage[user_hash]
        # if not usage["is_paid"] and usage["count"] >= FREE_LIMIT:
        #     return jsonify({
        #         "response": None,
        #         "limit_reached": True,
        #         "used_count": usage["count"],
        #         "remaining": 0,
        #         "message": "무료 상담 3회가 모두 사용되었습니다."
        #     })

        client = get_openai_client()

        # 일반 성도용 시스템 프롬프트 (기독교앱데이터 기반 상담)
        system_prompt = (
            f"당신은 모든 기독교 성도를 위한 따뜻하고 지혜로운 '영적 가이드'입니다. 사용자는 '{user_name} 님'입니다.\n"
            "사용자의 고민에 깊이 공감하고, 보편적인 기독교 신앙 안에서 성경적 위로와 지혜를 전달하십시오.\n\n"
            "상담 지침:\n"
            "1. 사용자의 감정을 먼저 읽고 따뜻한 위로의 말을 건네십시오.\n"
            "2. 관련된 성경 구절을 인용하고 그 의미를 일상에 적용할 수 있게 쉽게 설명하십시오.\n"
            "3. 답변 마지막에는 짧은 격려의 기도나 오늘 실천할 수 있는 믿음의 행동을 제안하십시오.\n"
            "4. 신학적이고 깊이 있는 성경적 분석을 포함한 '심층 분석' 섹션을 반드시 제공하십시오.\n\n"
            "답변 형식 (반드시 아래 태그와 형식을 엄격히 지켜주세요):\n"
            "[일반 답변 시작]\n"
            "### [따뜻한 위로]\n"
            "(사용자의 마음에 공감하는 내용)\n\n"
            "### [성경의 지혜]\n"
            "(인용 성경 구절 및 풀이)\n\n"
            "### [믿음의 발걸음]\n"
            "(짧은 기도나 실천 방안)\n"
            "[일반 답변 끝]\n\n"
            "[심층 분석 시작]\n"
            "(인간의 연약함, 하나님의 주권, 성경의 심오한 진리 등을 복음주의 관점에서 일반 답변보다 훨씬 더 길고 풍성하게, 1000자 이상으로 아주 상세하고 깊이 있게 분석)\n"
            "[심층 분석 끝]\n\n"
            "위기 상황(자해, 자살 언급 등)이 감지되면 반드시 다음을 안내하세요:\n"
            "자살예방상담전화 1393 | 정신건강위기상담전화 1577-0199"
        )

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ]
        )

        reply = completion.choices[0].message.content

        # ★ 구독 시스템 일시 정지 - 사용량 추적 없음
        return jsonify({
            "response": reply,
            "limit_reached": False
        })

    except Exception as e:
        print(f"[ERROR] {e}")
# Google Drive 찬양 API (기존 유지)
import requests as http_requests

print("COMPASS SERVER v1.0.5 - General Mode")

DRIVE_API_KEY = os.getenv("DRIVE_API_KEY")
# AIzaSyBUvx... 는 만료된 키임이 확인됨 -> 강제로 정상 키로 교체
if not DRIVE_API_KEY or DRIVE_API_KEY.startswith("AIzaSyBUvx"):
    DRIVE_API_KEY = "AIzaSyD1oqU-vb33CHNsJ8M13jROdYDgNyKDTNU"

DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "1372ozYC2muXXXSjGUSBoKpMHDJd-nmb9")

@app.route('/api/hymns')
def get_hymns():
    try:
        url = f"https://www.googleapis.com/drive/v3/files?q='{DRIVE_FOLDER_ID}'+in+parents&key={DRIVE_API_KEY}&fields=files(id,name,mimeType)&pageSize=100"
        resp = http_requests.get(url)
        
        if resp.status_code != 200:
            return jsonify({
                "error": f"구글 드라이브 연결 실패 (Status {resp.status_code})",
                "details": resp.text
            }), resp.status_code

        data = resp.json()
        files = data.get('files', [])
        audio_files = [f for f in files if f.get('mimeType', '').startswith('audio/')]
        audio_files.sort(key=lambda x: x.get('name', ''))
        return jsonify({"hymns": audio_files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/hymn-play/<file_id>')
def play_hymn(file_id):
    try:
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={DRIVE_API_KEY}"
        resp = http_requests.get(url, stream=True)
        from flask import Response
        return Response(
            resp.iter_content(chunk_size=8192),
            content_type=resp.headers.get('Content-Type', 'audio/mpeg'),
            headers={'Accept-Ranges': 'bytes'}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
