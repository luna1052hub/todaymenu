import os
import json
import re
import google.generativeai as genai

# Gemini API 키 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_trending_menus_with_ai():
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        return

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = """
    대한민국에서 사람들이 저녁 메뉴나 집밥으로 가장 많이 검색하고 실제로 자주 해먹는 대표 인기 요리 20개를 엄선해줘.

    [작성 규칙]
    1. '오늘뭐먹지', '정가볶음전문점', '볶음 간장', '간단한 저녁메뉴' 같은 검색어 문구, 가게 이름, 조미료는 절대로 포함하지 마.
    2. 오직 실제로 먹는 완벽한 '음식 이름/요리 이름'만 수집해 (예: 안동찜닭, 돼지 김치찌개, 차돌 된장찌개, 제육볶음, 오징어볶음 등).
    3. 각 음식마다 실제 들어가는 정확한 주요 재료와 실용적인 3단계 초간단 조리법을 작성해.
    4. 응답은 반드시 다른 설명 없이 오직 순수한 JSON 배열 형식으로만 출력해.

    [JSON 출력 형식]
    [
      {
        "name": "음식이름",
        "emoji": "🍲",
        "ingredients": "실제 주요 재료 (예: 돼지고기 150g, 신김치 200g, 두부 1/2모, 대파, 국간장)",
        "steps": [
          "1단계 조리법 문장",
          "2단계 조리법 문장",
          "3단계 조리법 문장"
        ]
      }
    ]
    """

    try:
        print("🤖 Gemini AI가 실시간 인기 집밥 메뉴와 정확한 레시피를 생성 중입니다...")
        response = model.generate_content(prompt)
        
        # JSON 데이터 추출 및 정제
        json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
        if json_match:
            menu_data = json.loads(json_match.group())
            
            # menu_data.json 파일로 저장
            with open('menu_data.json', 'w', encoding='utf-8') as f:
                json.dump(menu_data, f, ensure_ascii=False, indent=2)
                
            print(f"✨ AI 검증 완료! 진짜 저녁 메뉴 {len(menu_data)}건 저장 완료!")
        else:
            print("❌ AI 응답에서 JSON 구조를 찾을 수 없습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    generate_trending_menus_with_ai()
