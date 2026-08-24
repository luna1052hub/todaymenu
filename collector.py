import requests
import json
import urllib.parse
import re

def fetch_realtime_trending_recipes():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # 1. 수집 키워드 목록
    keywords = [
        "오늘저녁메뉴", "인기집밥레시피", "오늘뭐먹지", "저녁반찬추천",
        "찌개레시피", "볶음요리", "백종원레시피", "간단한저녁메뉴"
    ]
    
    # 2. 음식 접미사 기준
    food_suffixes = ['찌개', '볶음', '구이', '조림', '탕', '전골', '덮밥', '파스타', '찜', '국', '밥', '면', '무침', '전', '샐러드', '카레', '짜장', '돈까스', '치킨', '갈비']
    
    # 3. 불필요한 단어 및 접두어 제거 목록
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
                        
                        # 특수문자 제거
                        clean_word = re.sub(r'[^\w\s]', '', word).strip()
                        
                        # 차단 단어 제외
                        if any(ex in clean_word for ex in exclude_words):
                            continue
                            
                        # 음식 접미사 포함 여부 확인
                        if any(clean_word.endswith(suffix) or suffix in clean_word for suffix in food_suffixes):
                            clean_name = clean_word
                            
                            # '오늘뭐먹지', '레시피' 등 군더더기 단어 제거
                            for junk in junk_prefix_words:
                                clean_name = clean_name.replace(junk, "").strip()
                            
                            if len(clean_name) >= 2 and clean_name not in [t['name'] for t in trending_items]:
                                trending_items.append({
                                    "name": clean_name,
                                    "emoji": "🍲",
                                    "ingredients": f"'{clean_name}' 최신 검색 트렌드 인기 요리입니다. 주재료 및 양념 준비",
                                    "steps": [
                                        f"포털에서 최근 '{clean_name}' 검색 및 관심도가 높아진 요리입니다.",
                                        "하단 버튼을 눌러 최근 올라온 생생한 영상 및 블로그 레시피를 확인하세요.",
                                        "맛있게 요리하여 완성해 보세요!"
                                    ]
                                })
        except Exception as e:
            print(f"수집 오류: {e}")

    # 파일 저장
    with open('menu_data.json', 'w', encoding='utf-8') as f:
        json.dump(trending_items, f, ensure_ascii=False, indent=2)
        
    print(f"정제된 순수 메뉴 {len(trending_items)}건 수집 완료!")

if __name__ == "__main__":
    fetch_realtime_trending_recipes()
