import requests
import json
import urllib.parse
import re

def generate_recipe_detail(name):
    """메뉴 이름에 맞춰 실제 재료와 3단계 조리법을 생성하는 함수"""
    if '찌개' in name or '국' in name:
        ingredients = f"{name} 주재료, 두부, 대파, 양파, 마늘, 국간장/된장"
        steps = [
            f"주재료와 파, 양파, 두부를 먹기 좋은 크기로 손질합니다.",
            f"냄비에 육수를 붓고 준비한 {name} 재료와 양념을 넣어 푹 끓입니다.",
            f"간을 맞춘 뒤 두부와 대파를 넣고 한소끔 더 끓여 완성합니다."
        ]
    elif '볶음' in name:
        ingredients = f"{name} 주재료, 양파, 대파, 마늘, 고추장/간장 양념장"
        steps = [
            f"주재료와 양파, 대파 등 야채를 썰어 준비합니다.",
            f"양념장을 만들어 재료와 함께 오목한 팬에 넣습니다.",
            f"센 불에서 양념이 잘 베이도록 불향 나게 볶아냅니다."
        ]
    elif '구이' in name:
        ingredients = f"{name} 주재료, 식용유, 소금, 후추, 와사비/간장"
        steps = [
            f"재료의 핏물이나 물기를 제거하고 소금, 후추로 밑간합니다.",
            f"달군 팬에 기름을 두르고 중불에서 노릇하게 구워냅니다.",
            f"먹기 좋은 크기로 잘라 소스와 함께 차려냅니다."
        ]
    elif '전골' in name or '탕' in name:
        ingredients = f"{name} 주재료, 버섯류, 쑥갓, 대파, 전골 육수"
        steps = [
            f"전골 냄비에 버섯, 야채와 {name} 재료를 예쁘게 담습니다.",
            f"준비한 전골 육수를 자작하게 붓고 센 불로 끓입니다.",
            f"재료가 익으면 불을 줄이고 따뜻하게 즐깁니다."
        ]
    elif '덮밥' in name or '밥' in name:
        ingredients = f"따뜻한 밥 1공기, {name} 주재료, 계란, 김가루, 참기름"
        steps = [
            f"{name}에 들어갈 주재료를 달콤 짭조름하게 볶아 준비합니다.",
            f"그릇에 따뜻한 밥을 담고 볶은 재료와 스크램블 계란을 올립니다.",
            f"김가루와 참기름을 뿌려 고소하게 쓱쓱 비벼 먹습니다."
        ]
    else:
        ingredients = f"{name} 주재료, 양파, 대파, 마늘, 기본 양념장"
        steps = [
            f"{name}에 필요한 주요 재료를 씻어 먹기 좋게 손질합니다.",
            f"양념장과 재료를 함께 넣어 양념이 쏙 배도록 조리합니다.",
            f"예쁜 그릇에 담아 고소한 통깨를 뿌려 완성합니다."
        ]
    return ingredients, steps

def fetch_realtime_trending_recipes():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    keywords = [
        "오늘저녁메뉴", "인기집밥레시피", "오늘뭐먹지", "저녁반찬추천",
        "찌개레시피", "볶음요리", "백종원레시피", "간단한저녁메뉴"
    ]
    
    food_suffixes = ['찌개', '볶음', '구이', '조림', '탕', '전골', '덮밥', '파스타', '찜', '국', '밥', '면', '무침', '전', '샐러드', '카레', '짜장', '돈까스', '치킨', '갈비']
    junk_prefix_words = ['오늘뭐먹지', '오늘저녁메뉴', '인기집밥레시피', '저녁반찬추천', '백종원레시피', '간단한저녁메뉴', '만들기', '레시피', '추천', '요리']
    exclude_words = ['룰렛', '리스트', '해줘', '외식', '배달', '한식', '표', '도서', '모음', '어플', '북', '책', '유튜브', '간편식', '식탁', '블록국', '종류', '순위', '모바일', '게임', '사이트']

    trending_items = []

    for kw in keywords:
        encoded_kw = urllib.parse.quote(kw)
        url = f"https://ac.search.naver.com/nx/ac?q={encoded_kw}&st=100&r_format=json&q_enc=UTF-8&r_enc=UTF-8"
        
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                items = data.get('items', [])
                for group in items:
                    for item in group:
                        word = item[0]
                        clean_word = re.sub(r'[^\w\s]', '', word).strip()
                        
                        if any(ex in clean_word for ex in exclude_words):
                            continue
                            
                        if any(clean_word.endswith(suffix) or suffix in clean_word for suffix in food_suffixes):
                            clean_name = clean_word
                            for junk in junk_prefix_words:
                                clean_name = clean_name.replace(junk, "").strip()
                            
                            if len(clean_name) >= 2 and clean_name not in [t['name'] for t in trending_items]:
                                ingredients, steps = generate_recipe_detail(clean_name)
                                trending_items.append({
                                    "name": clean_name,
                                    "emoji": "🍲",
                                    "ingredients": ingredients,
                                    "steps": steps
                                })
        except Exception as e:
            print(f"수집 오류: {e}")

    with open('menu_data.json', 'w', encoding='utf-8') as f:
        json.dump(trending_items, f, ensure_ascii=False, indent=2)
        
    print(f"정제 완료된 메뉴 {len(trending_items)}건 저장 완료!")

if __name__ == "__main__":
    fetch_realtime_trending_recipes()
