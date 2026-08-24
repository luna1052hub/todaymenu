import requests
from bs4 import BeautifulSoup
import json

def fetch_google_trends_recipes():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 구글 트렌드 대한민국 실시간 급상승 RSS
    google_rss_url = "https://trends.google.co.kr/trends/trendingsearches/daily/rss?geo=KR"
    
    trending_keywords = []
    
    try:
        res = requests.get(google_rss_url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'xml')
            items = soup.find_all('item')
            
            for item in items:
                title = item.find('title').get_text(strip=True)
                # 구글 실시간 급상승어 추출
                trending_keywords.append({
                    "name": title,
                    "emoji": "🔥",
                    "ingredients": f"'{title}' 관련 검색 급상승 트렌드 재료",
                    "steps": [
                        f"1. '{title}' 관련 실시간 인기도가 상승 중입니다.",
                        "2. 유튜브나 인스타그램 버튼을 눌러 생생한 조리법을 확인하세요.",
                        "3. 맛있게 요리하여 완성합니다!"
                    ]
                })
    except Exception as e:
        print(f"구글 트렌드 RSS 수집 실패: {e}")

    # 기본 메뉴 목록을 완전히 없애고, 오직 수집된 데이터만 저장합니다.
    with open('menu_data.json', 'w', encoding='utf-8') as f:
        json.dump(trending_keywords, f, ensure_ascii=False, indent=2)
        
    print(f"구글 트렌드 실시간 데이터 {len(trending_keywords)}건 저장 완료!")

if __name__ == "__main__":
    fetch_google_trends_recipes()
