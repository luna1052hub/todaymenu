import json
import pandas as pd
from pytrends.request import TrendReq
from recipes_db import RECIPE_DATABASE

# 기준점이 될 앵커 키워드
ANCHOR_QUERY = "김치찌개"

def fetch_google_trends_normalized():
    print("🔍 [기준점 보정 방식] 구글 트렌드 정밀 상대 지수 측정 시작...")
    
    pytrend = TrendReq(hl='ko-KR', tz=540)
    
    # DB에서 앵커 키워드를 제외한 나머지 수집 대상 목록
    target_items = [item for item in RECIPE_DATABASE if item["query"] != ANCHOR_QUERY]
    
    # 앵커 항목 자체 찾기
    anchor_item = next((item for item in RECIPE_DATABASE if item["query"] == ANCHOR_QUERY), None)
    
    normalized_scores = {}
    
    # 앵커 항목 기본점수 초기화 (기준값 1.0)
    if anchor_item:
        normalized_scores[ANCHOR_QUERY] = {
            "menu": anchor_item,
            "raw_score": 0,
            "final_score": 0
        }

    try:
        # 4개씩 나누어 앵커 키워드(1개)와 함께 총 5개씩 조합 수집
        chunk_size = 4
        queries_list = [item["query"] for item in target_items]
        
        anchor_scores = []  # 앵커 키워드의 청크별 스코어 기록
        chunk_raw_results = []

        for i in range(0, len(queries_list), chunk_size):
            chunk = queries_list[i:i+chunk_size]
            payload_queries = [ANCHOR_QUERY] + chunk  # 항상 앵커 키워드 포함 (총 5개)
            
            pytrend.build_payload(kw_list=payload_queries, timeframe='now 7-d', geo='KR')
            df = pytrend.interest_over_time()
            
            if not df.empty:
                recent_3days = df.tail(3)
                means = recent_3days.mean()
                
                anchor_score_in_chunk = means.get(ANCHOR_QUERY, 1.0)
                # 0으로 나누는 상황 방지
                if anchor_score_in_chunk == 0:
                    anchor_score_in_chunk = 1.0
                    
                anchor_scores.append(anchor_score_in_chunk)
                
                # 청크 내부 상대 스코어 기록
                chunk_data = {}
                for q in payload_queries:
                    chunk_data[q] = means.get(q, 0)
                
                chunk_raw_results.append({
                    "anchor_score": anchor_score_in_chunk,
                    "data": chunk_data
                })

        # 평균 앵커 점수를 기준으로 전체 보정 계수 산출 및 정규화
        avg_anchor_score = sum(anchor_scores) / len(anchor_scores) if anchor_scores else 1.0
        
        # 앵커 항목의 최종 스코어 반영
        if anchor_item:
            normalized_scores[ANCHOR_QUERY]["final_score"] = avg_anchor_score

        for res in chunk_raw_results:
            chunk_anchor = res["anchor_score"]
            # 앵커 대비 비율 보정 계수
            ratio = avg_anchor_score / chunk_anchor if chunk_anchor > 0 else 1.0
            
            for q, raw_val in res["data"].items():
                if q == ANCHOR_QUERY:
                    continue
                
                db_item = next((m for m in RECIPE_DATABASE if m["query"] == q), None)
                if db_item:
                    # 앵커 기준값으로 스케일 변환된 정규화 스코어
                    adjusted_score = raw_val * ratio
                    normalized_scores[q] = {
                        "menu": db_item,
                        "final_score": adjusted_score
                    }

    except Exception as e:
        print(f"⚠️ 구글 트렌드 수집 중 예외 발생 (기본 DB 순서 사용): {e}")

    # 정규화 스코어 기반 내림차순 정렬
    if len(normalized_scores) > 0:
        sorted_items = sorted(normalized_scores.values(), key=lambda x: x["final_score"], reverse=True)
        final_list = [item["menu"] for item in sorted_items]
    else:
        final_list = RECIPE_DATABASE

    # 1위~4위 트렌드 뱃지 및 일반 뱃지 부여
    for idx, item in enumerate(final_list, 1):
        if idx <= 4:
            item["rank_badge"] = f"🏆 트렌드 {idx}위"
        else:
            item["rank_badge"] = f"⭐ 추천 메뉴"

    return final_list

def update_json():
    sorted_menu_list = fetch_google_trends_normalized()
    
    with open('menu_data.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_menu_list, f, ensure_ascii=False, indent=2)

    print(f"✅ 정규화 보정 완료된 30개 순위 메뉴 저장 완료!")

if __name__ == "__main__":
    update_json()
