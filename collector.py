import os
import json
import re
from datetime import datetime
import google.generativeai as genai

# GitHub Secrets에 등록된 GEMINI_API_KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def fetch_today_trending_menus():
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다. GitHub Secrets를 확인해 주세요.")
        return

    # 오늘 날짜 및 요일 자동 파악
    now = datetime.now()
    today_str = now.strftime("%Y년 %m월 %d일")

    genai.configure(api_key=GEMINI_API_KEY)
    
    # gemini-2.5-flash 최신 모델 사용
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = f"""
    오늘 날짜는 [{today_str}] 입니다.
    대한민국에서 오늘 날짜와 계절감(날씨/계절)을 고려했을 때, 포털 사이트나 SNS에서 실제 검색량이 급상승하고 사람들이 요즘 가장 많이 해먹는 '인기 집밥/저녁 메뉴 20가지'를 엄선해 주세요.

    [엄격한 작성 규칙]
    1. '오늘뭐먹지', '정가볶음전문점', '볶음 간장', '간단한 저녁메뉴', '룰렛' 같은 검색용 단어나 가게 이름, 조미료는 절대로 포함하지 마세요.
    2. 오직 실제 음식/요리 명칭만 수집하세요 (예: 삼계탕, 차돌 된장찌개, 오이냉국, 제육볶음, 닭볶음탕 등).
    3. 추상적인 '주재료' 같은 표현은 절대 쓰지 말고, 각 요리에 실제로 들어가는 정확한 주요 재료와 양념(예: 돼지고기 150g, 신김치 200g, 두부 1/2모, 대파, 국간장)을 명시하세요.
    4. 조리법은 진짜 따라할 수 있는 실용적인 3단계 초간단 레시피로 작성하세요.
    5. 응답은 다른 설명이나 서두 없이 오직 순수한 JSON 배열 형식만 출력하세요.

    [JSON 형식]
    [
      {{
        "name": "음식이름",
        "emoji": "🍲",
        "ingredients": "실제 주요 재료 및 양념 목록",
        "steps": [
          "1단계 조리법 문장",
          "2단계 조리법 문장",
          "3단계 조리법 문장"
        ]
      }}
    ]
    """

    try:
        print(f"🤖 오늘 날짜({today_str}) 기준 검색 트렌드 메뉴 및 AI 레시피 분석 시작...")
        response = model.generate_content(prompt)
        
        # JSON 데이터만 추출
        json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
        if json_match:
            menu_data = json.loads(json_match.group())
            
            # menu_data.json 저장
            with open('menu_data.json', 'w', encoding='utf-8') as f:
                json.dump(menu_data, f, ensure_ascii=False, indent=2)
                
            print(f"✅ [{today_str}] 기준 트렌드 메뉴 {len(menu_data)}건 생성 및 저장 완료!")
        else:
            print("❌ AI 응답에서 JSON 구조를 찾지 못했습니다.")

    except Exception as e:
        print(f"❌ API 호출 중 오류 발생: {e}")

if __name__ == "__main__":
    fetch_today_trending_menus()
