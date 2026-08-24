import requests
from bs4 import BeautifulSoup
import json
import random

def fetch_trending_keywords():
    """네이버 데이터랩 및 뉴스 검색 기반 최근 인기 집밥 키워드 수집"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 네이버 인기 레시피/집밥 관련 검색 트렌드 수집 대상 URL
    url = "https://search.naver.com/search.naver?where=nexearch&query=오늘저녁메뉴추천"
    
    trending_items = []
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 검색 연관어 및 블로그 인기 주제어 추출
        keywords = soup.select(".lst_related _related_keywords_list li, .api_txt_lines")
        
        for k in keywords:
            text = k.get_text(strip=True)
            # 집밥 메뉴에 적합한 단어 필터링
            if any(word in text for word in ['찌개', '볶음', '구이', '조림', '탕', '전골', '덮밥', '파스타', '찜']):
                clean_name = text.replace("만들기", "").replace("레시피", "").strip()
                if clean_name and clean_name not in [item['name'] for item in trending_items]:
                    trending_items.append({
                        "name": clean_name,
                        "emoji": "🍲",
                        "ingredients": f"{clean_name} 주재료, 양파, 대파, 마늘, 기본 양념장",
                        "steps": [
                            f"1. {clean_name}에 필요한 주요 재료를 먹기 좋은 크기로 손질합니다.",
                            "2. 냄비나 팬에 양념장과 함께 재료를 넣고 조리합니다.",
                            "3. 간을 맞추고 맛있게 완성하여 그릇에 담아냅니다."
                        ]
                    })
    except Exception as e:
        print(f"수집 실패: {e}")
        
    # 기본 인기 트렌드 메뉴 백업 데이터 (최소 개수 보장)
    default_trending = [
        {"name": "차돌된장찌개", "emoji": "🍲", "ingredients": "차돌박이 100g, 된장, 애호박, 두부, 청양고추", "steps": ["1. 차돌박이를 볶아 고소한 기름을 만듭니다.", "2. 물과 된장을 풀고 야채를 넣습니다.", "3. 두부와 고추를 넣고 자작하게 끓입니다."]},
        {"name": "돼지고기 김치찌개", "emoji": "🥘", "ingredients": "돼지고기 150g, 신김치 200g, 두부, 파, 국간장", "steps": ["1. 돼지고기를 냄비에 볶아 기름을 냅니다.", "2. 신김치를 넣고 함께 볶아줍니다.", "3. 물을 붓고 푹 끓여 두부로 마무리합니다."]},
        {"name": "제육볶음", "emoji": "🥩", "ingredients": "돼지 불고깃감 300g, 고추장, 간장, 양파, 대파", "steps": ["1. 고추장 양념장을 만듭니다.", "2. 고기와 양념을 함께 재워둡니다.", "3. 센 불에서 불향 나게 볶아냅니다."]},
        {"name": "닭볶음탕", "emoji": "🍗", "ingredients": "닭 1마리, 감자, 당근, 고추장, 고춧가루, 간장", "steps": ["1. 닭을 먼저 데쳐 불순물을 제거합니다.", "2. 양념장과 야채를 넣고 끓입니다.", "3. 국물이 자작해질 때까지 졸입니다."]},
        {"name": "소불고기 전골", "emoji": "🍲", "ingredients": "소불고기 200g, 버섯류, 당면, 간장, 설탕", "steps": ["1. 불고기에 간장 양념을 해둡니다.", "2. 전골냄비에 버섯, 당면과 함께 담습니다.", "3. 육수를 자작하게 붓고 끓입니다."]},
        {"name": "오징어 볶음", "emoji": "🦑", "ingredients": "오징어 1마리, 양배추, 당근, 고추장, 고춧가루", "steps": ["1. 오징어와 야채를 썰어 준비합니다.", "2. 양념장을 만듭니다.", "3. 센 불에서 채즙이 나오지 않게 빠르게 볶아냅니다."]}
    ]
    
    # 수집 데이터와 기본 데이터 통합
    final_list = trending_items + [d for d in default_trending if d['name'] not in [t['name'] for t in trending_items]]
    
    # JSON 파일 저장
    with open('menu_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)
    print("메뉴 데이터 수집 완료!")

if __name__ == "__main__":
    fetch_trending_keywords()
