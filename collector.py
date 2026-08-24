import requests
from bs4 import BeautifulSoup
import json

def fetch_google_trends():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 구글 트렌드 대한민국 실시간 급상승 RSS
    url = "https://trends.google.co.kr/trends/trendingsearches/daily/rss?geo=KR"
    
    trending_list = []
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'xml')
            items = soup.find_all('item')
            
            for item in items:
                title = item.find('title').get_text(strip=True)
                trending_list.append({
                    "name": title,
                    "emoji": "🔥",
                    "ingredients": f"'{title}' 관련 실시간 구글 급상승 검색 트렌드 키워드입니다.",
                    "steps": [
                        f"1. 현재 구글에서 '{title}' 검색량이 급상승 중입니다.",
                        "2. 하단의 유튜브/인스타그램 버튼을 누르면 관련 생생한 최신 영상 및 사진을 보실 수 있습니다.",
                        "3. 트렌디한 저녁 아이디어를 얻어보세요!"
                    ]
                })
    except Exception as e:
        print(f"수집 예외: {e}")

    # 파일 저장 (수집된 리스트 저장)
    with open('menu_data.json', 'w', encoding='utf-8') as f:
        json.dump(trending_list, f, ensure_ascii=False, indent=2)
        
    print(f"데이터 {len(trending_list)}건 저장 완료!")

if __name__ == "__main__":
    fetch_google_trends()
