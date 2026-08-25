import json
import pandas as pd
from datetime import datetime, timedelta
from pytrends.request import TrendReq

# 1. 완벽한 집밥 메뉴 & 레시피 데이터베이스 (DB)
# 메뉴를 계속 늘리고 싶으시면 아래 형성에 맞춰 계속 추가해 주시면 됩니다.
RECIPE_DATABASE = [
    {
        "name": "돼지 김치찌개", "query": "김치찌개", "emoji": "🥘",
        "ingredients": "돼지고기 목살 150g, 신김치 200g, 두부 1/2모, 대파 1대, 국간장 1스푼, 다진 마늘 1스푼",
        "steps": ["돼지고기와 신김치를 냄비에 볶아 고기 기름을 만듭니다.", "물 500ml를 붓고 중불에서 15분간 푹 끓입니다.", "두부와 대파를 올리고 간을 맞춰 한소끔 더 끓여 완성합니다."]
    },
    {
        "name": "차돌 된장찌개", "query": "된장찌개", "emoji": "🍲",
        "ingredients": "차돌박이 100g, 된장 2스푼, 애호박 1/2개, 두부 1/2모, 버섯, 청양고추",
        "steps": ["차돌박이를 먼저 냄비에 구워 기름을 냅니다.", "물 400ml와 된장을 풀고 애호박, 버섯을 넣습니다.", "두부와 청양고추를 넣고 자작하게 더 끓여냅니다."]
    },
    {
        "name": "매콤 제육볶음", "query": "제육볶음", "emoji": "🥩",
        "ingredients": "돼지고기 불고깃감 300g, 양파 1/2개, 대파, 고추장 2스푼, 고춧가루, 간장, 설탕",
        "steps": ["고추장, 간장, 설탕, 마늘로 양념장을 만듭니다.", "돼지고기에 양념을 재운 뒤 야채를 준비합니다.", "달군 팬에 센 불로 불향이 나도록 빠르게 볶아냅니다."]
    },
    {
        "name": "안동찜닭", "query": "찜닭", "emoji": "🍗",
        "ingredients": "토막 닭 1마리, 불린 당면 100g, 감자 2개, 당근, 대파, 진간장, 굴소스",
        "steps": ["닭을 데쳐 불순물을 씻어내고 당면은 불려둡니다.", "냄비에 닭, 감자, 당근, 간장 양념을 넣고 졸입니다.", "불린 당면을 넣고 국물이 자작해질 때까지 졸입니다."]
    },
    {
        "name": "오징어 볶음", "query": "오징어볶음", "emoji": "🦑",
        "ingredients": "오징어 1마리, 양배추, 양파, 대파, 고추장 1스푼, 고춧가루, 간장",
        "steps": ["오징어와 야채를 큼직하게 손질합니다.", "양념장을 만들어 센 불에서 빠르게 볶아냅니다.", "통깨를 뿌려 고소하게 마무리합니다."]
    },
    {
        "name": "닭볶음탕", "query": "닭볶음탕", "emoji": "🍗",
        "ingredients": "토막 닭 1마리, 감자 2개, 당근, 양파, 설탕, 고추장, 고춧가루, 간장",
        "steps": ["데친 닭에 물을 붓고 설탕을 먼저 넣어 끓입니다.", "감자, 야채와 고추장, 간장 양념을 넣습니다.", "국물이 자작해질 때까지 푹 졸여냅니다."]
    },
    {
        "name": "소불고기 전골", "query": "불고기", "emoji": "🍲",
        "ingredients": "소불고기 200g, 팽이버섯, 표고버섯, 당면, 대파, 진간장, 설탕",
        "steps": ["소고기는 간장, 설탕, 참기름 양념에 재워둡니다.", "전골 냄비에 버섯, 야채, 당면과 함께 담습니다.", "자작하게 육수를 붓고 끓여 따뜻하게 즐깁니다."]
    },
    {
        "name": "우삼겹 숙주볶음", "query": "숙주볶음", "emoji": "🥩",
        "ingredients": "우삼겹 200g, 숙주 1봉지, 대파, 다진 마늘, 굴소스 1.5스푼",
        "steps": ["우삼겹과 마늘, 대파를 넣고 노릇하게 볶습니다.", "고기가 익으면 굴소스를 넣어 간을 맞춥니다.", "숙주를 넣고 센 불에서 1분간 빠르게 볶아냅니다."]
    }
]

def fetch_google_trends_top4():
    """구글 트렌드 기준 최근 3일간 평균 검색량 계산 후 1~4위 추출"""
    print("🔍 구글 트렌드 최근 3일간 평균 검색 트렌드 분석 시작...")
    
    # 한국 지역(KR) 설정
    pytrend = TrendReq(hl='ko-KR', tz=540)
    
    # DB에 있는 대표 검색 키워드 추출
    queries = [item["query"] for item in RECIPE_DATABASE]
    
    scored_items = []

    # 구글 트렌드는 한번에 최대 5개 키워드 비교 가능하므로 나누어 측정
    try:
        for i in range(0, len(queries), 5):
            chunk_queries = queries[i:i+5]
            
            # 최근 3일간 데이터 요청 (today 3-d)
            pytrend.build_payload(kw_list=chunk_queries, timeframe='now 7-d', geo='KR')
            df = pytrend.interest_over_time()
            
            if not df.empty:
                # 최근 3일(마지막 3개 행) 데이터 평균 계산
                recent_3days = df.tail(3)
                means = recent_3days.mean()
                
                for q, score in means.items():
                    if q in chunk_queries:
                        # 원래 DB 항목과 매핑
                        db_item = next((m for m in RECIPE_DATABASE if m["query"] == q), None)
                        if db_item:
                            scored_items.append({"menu": db_item, "score": score})
    except Exception as e:
        print(f"⚠️ 구글 트렌드 수집 예외 발생 (기본 순서 적용): {e}")
        return RECIPE_DATABASE[:4]

    # 검색량 평균 스코어 기준 내림차순 정렬
    if scored_items:
        scored_items.sort(key=lambda x: x["score"], reverse=True)
        top4 = [item["menu"] for item in scored_items[:4]]
        return top4

    return RECIPE_DATABASE[:4]

def update_top4_json():
    top4 = fetch_google_trends_top4()
    
    # json 저장
    with open('menu_data.json', 'w', encoding='utf-8') as f:
        json.dump(top4, f, ensure_ascii=False, indent=2)

    print("✅ 구글 트렌드 3일 평균 1~4위 메뉴 추출 및 저장 완료!")

if __name__ == "__main__":
    update_top4_json()
