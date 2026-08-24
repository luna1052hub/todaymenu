import requests
from bs4 import BeautifulSoup
import json
import re

def fetch_trending_keywords():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 네이버 키워드 및 트렌드 데이터 수집
    url = "https://search.naver.com/search.naver?where=nexearch&query=주간+인기+집밥+레시피"
    trending_items = []
    
    # 기본 검증된 인기 메뉴 리스트 (최소 4개 이상 보장)
    base_menus = [
        {"name": "돼지 김치찌개", "emoji": "🥘", "ingredients": "돼지고기 150g, 신김치 200g, 두부", "steps": ["1. 고기와 김치를 볶습니다.", "2. 물을 붓고 끓입니다.", "3. 두부와 파를 넣습니다."]},
        {"name": "차돌 된장찌개", "emoji": "🍲", "ingredients": "차돌박이, 된장, 애호박, 두부", "steps": ["1. 고기를 구워 기름을 냅니다.", "2. 물과 된장을 풀고 야채를 넣습니다.", "3. 두부를 넣고 끓입니다."]},
        {"name": "매콤 제육볶음", "emoji": "🥩", "ingredients": "돼지 불고깃감 300g, 고추장 양념, 양파", "steps": ["1. 양념장에 고기를 재웁니다.", "2. 야채를 썰어 준비합니다.", "3. 센 불에 불향 나게 볶습니다."]},
        {"name": "소불고기 전골", "emoji": "🍲", "ingredients": "소불고기 200g, 버섯, 당면, 간장", "steps": ["1. 고기에 간장 양념을 합니다.", "2. 냄비에 버섯과 함께 담습니다.", "3. 육수를 붓고 끓입니다."]},
        {"name": "닭볶음탕", "emoji": "🍗", "ingredients": "닭 1마리, 감자, 당근, 고추장 양념", "steps": ["1. 닭을 먼저 데쳐냅니다.", "2. 양념과 야채를 넣고 끓입니다.", "3. 국물이 자작해지도록 졸입니다."]},
        {"name": "오징어 볶음", "emoji": "🦑", "ingredients": "오징어 1마리, 양배추, 고추장 양념", "steps": ["1. 오징어와 야채를 듬성듬성 땁니다.", "2. 양념장을 만듭니다.", "3. 센 불에서 빠르게 볶아냅니다."]}
    ]
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 키워드 데이터 추출 시도
        elements = soup.select(".lst_related _related_keywords_list li, .api_txt_lines")
        for el in elements:
            txt = el.get_text(strip=True)
            clean = re.sub(r'[^\w\s]', '', txt).replace("만들기", "").replace("레시피", "").strip()
            if any(w in clean for w in ['찌개', '볶음', '구이', '조림', '탕', '전골']):
                if clean and clean not in [m['name'] for m in trending_items]:
                    trending_items.append({
                        "name": clean,
                        "emoji": "🍳",
                        "ingredients": f"{clean} 주재료, 양파, 대파, 마늘",
                        "steps": ["1. 재료를 손질합니다.", "2. 양념과 함께 조리합니다.", "3. 맛있게 완성합니다."]
                    })
    except Exception as e:
        print(f"크롤링 예외: {e}")

    # 데이터 통합 (최소 4개 이상 무조건 확보)
    final_list = trending_items + [b for b in base_menus if b['name'] not in [t['name'] for t in trending_items]]
    
    with open('menu_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    fetch_trending_keywords()
