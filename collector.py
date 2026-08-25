import json
import pandas as pd
from pytrends.request import TrendReq
from recipes_db import RECIPE_DATABASE

def fetch_google_trends_sorted():
    print("🔍 구글 트렌드 3일 평균 검색량 기준 30개 전체 순위 집계 시작...")
    
    pytrend = TrendReq(hl='ko-KR', tz=540)
    queries = [item["query"] for item in RECIPE_DATABASE]
    scored_items = []

    try:
        # 5개씩 나누어 구글 트렌드 수집
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
        print(f"⚠️ 구글 트렌드 수집 예외 발생: {e}")

    # 검색량 점수 높은 순으로 30개 전체 정렬
    if scored_items:
        scored_items.sort(key=lambda x: x["score"], reverse=True)
        sorted_list = [item["menu"] for item in scored_items]
    else:
        sorted_list = RECIPE_DATABASE

    # 순위 표기 부여 (1위~4위는 트렌드 순위 표기)
    for idx, item in enumerate(sorted_list, 1):
        if idx <= 4:
            item["rank_badge"] = f"🏆 트렌드 {idx}위"
        else:
            item["rank_badge"] = f"⭐ 추천 메뉴"

    return sorted_list

def update_json():
    all_sorted_menus = fetch_google_trends_sorted()
    
    with open('menu_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_sorted_menus, f, ensure_ascii=False, indent=2)

    print(f"✅ 검색 순위별 전체 {len(all_sorted_menus)}개 메뉴 저장 완료!")

if __name__ == "__main__":
    update_json()
