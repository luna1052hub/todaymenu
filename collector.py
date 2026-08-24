import requests
import json
import urllib.parse

def fetch_realtime_trending_recipes():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # 1. 포털 연관어/급상승 키워드 추출 API
    keywords = ["오늘저녁메뉴", "집밥레시피", "인기요리", "간편식"]
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
                        # '만들기', '레시피' 등 불필요한 단어 정제
                        clean_word = word.replace("만들기", "").replace("레시피", "").replace("추천", "").strip()
                        
                        # 메뉴 데이터로 적합한 2자 이상의 단어만 수집
                        if len(clean_word) >= 2 and clean_word not in [t['name'] for t in trending_items]:
                            trending_items.append({
                                "name": clean_word,
                                "emoji": "🔥",
                                "ingredients": f"'{clean_word}' 검색 트렌드 급상승 메뉴입니다. 주재료 및 양념 준비",
                                "steps": [
                                    f"1. 포털 검색창에서 최근 '{clean_word}' 검색량이 급상승 중입니다.",
                                    "2. 하단 버튼을 눌러 최근 올라온 생생한 영상 및 블로그 레시피를 확인하세요.",
                                    "3. 맛있는 집밥을 완성해 보세요!"
                                ]
                            })
        except Exception as e:
            print(f"키워드 수집 실패: {e}")

    # 파일 저장
    with open('menu_data.json', 'w', encoding='utf-8') as f:
        json.dump(trending_items, f, ensure_ascii=False, indent=2)
        
    print(f"실시간 급상승 메뉴 {len(trending_items)}건 수집 완료!")

if __name__ == "__main__":
    fetch_realtime_trending_recipes()
