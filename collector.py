import json
import pandas as pd
from pytrends.request import TrendReq
# 우리가 새로 만든 30개 메뉴 DB 불러오기
from recipes_db import RECIPE_DATABASE

def fetch_google_trends_top4():
    print("🔍 [30개 메뉴 DB 연동] 구글 트렌드 3일 평균 검색량 측정 시작...")
    
    pytrend = TrendReq(hl='ko-KR', tz=540)
    queries = [item["query"] for item in RECIPE_DATABASE]
    
    scored_items = []

    try:
        # 구글 트렌드 5개씩 나누어 분석
        for i in range(0, len(queries), 5):
            chunk_queries = queries[i:i+5]
            
            pytrend.build_payload(kw_list=chunk_queries, timeframe='now 7-d', geo='KR')
            df = pytrend.interest_over_time()
            
            if not df.empty:
                recent_3days = df.tail(3)
                means = recent_3days.mean()
                
                for q, score in means.items():
                    if q in chunk_queries:
                        db_item = next((m for m in RECIPE_DATABASE if m["query"] == q), None)
                        if db_item:
                            scored_items.append({"menu": db_item, "score": score})
    except Exception as e:
        print(f"⚠️ 구글 트렌드 수집 예외 발생 (기본 4개 반환): {e}")
        return RECIPE_DATABASE[:4]

    if scored_items:
        # 검색 점수 높은 순으로 정렬
        scored_items.sort(key=lambda x: x["score"], reverse=True)
        top4 = [item["menu"] for item in scored_items[:4]]
        return top4

    return RECIPE_DATABASE[:4]

def update_top4_json():
    top4 = fetch_google_trends_top4()
    
    with open('menu_data.json', 'w', encoding='utf-8') as f:
        json.dump(top4, f, ensure_ascii=False, indent=2)

    print("✅ 30개 DB 중 구글 검색량 상위 1~4위 추출 완료!")

if __name__ == "__main__":
    update_top4_json()
