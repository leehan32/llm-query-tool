# 최종 자연편향 데이터셋을 한번에 생성하는 전체 코드 (수정사항 모두 포함)

import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import zipfile

# 기본 정의
NUM_STUDENTS = 100
NUM_RESTAURANTS = 10
START_YEAR = 2024

# 이름 및 음식 종류 정의
korean_last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임']
korean_first_names = ['민준', '서연', '지후', '하은', '도윤', '예린', '지민', '수아', '현우', '윤서']
restaurant_prefixes = ['맛', '불', '청', '행', '고', '황', '참', '왕', '동', '옛']
restaurant_suffixes = ['집', '마루', '면', '장', '한', '방', '상', '당', '촌', '향']
korean_food_types = ['피자', '햄버거', '한식', '분식', '초밥', '중식', '카페', '베이커리']
food_descriptions = {
    '피자': '이탈리아식 피자 전문점',
    '햄버거': '즉석 햄버거 전문점',
    '한식': '집밥 스타일의 한식',
    '분식': '떡볶이, 순대 등 분식류',
    '초밥': '일본식 초밥 제공',
    '중식': '중국요리 전문점',
    '카페': '커피 및 디저트 제공',
    '베이커리': '빵과 케이크 전문점'
}

# (1) 학생 테이블 생성
students_data = []
for i in range(1, NUM_STUDENTS + 1):
    name = f"{random.choice(korean_last_names)}{random.choice(korean_first_names)}"
    age = random.randint(16, 30)
    sex = random.choice(['남', '여'])
    major = random.randint(100, 6000)
    advisor = random.randint(1000, 9999)
    city = random.choice(['서울', '부산', '대구', '광주', '대전', '수원', '인천'])
    students_data.append([i, name, age, sex, major, advisor, city])
students_df = pd.DataFrame(students_data, columns=["학생ID", "이름", "나이", "성별", "전공코드", "지도교수", "거주도시"])

# (2) 식당 테이블
restaurants_data = []
for i in range(1, NUM_RESTAURANTS + 1):
    name = f"{random.choice(restaurant_prefixes)}{random.choice(restaurant_suffixes)}"
    address = f"{100 + i} 도로, 서울"
    rating = round(min(max(random.gauss(4.0, 0.4), 1), 5), 1)
    restaurants_data.append([i, name, address, rating])
restaurants_df = pd.DataFrame(restaurants_data, columns=["식당ID", "식당이름", "주소", "평점"])

# (3) 식당 유형 테이블
rest_types_df = pd.DataFrame(
    [[i + 1, food, food_descriptions[food]] for i, food in enumerate(korean_food_types)],
    columns=["유형ID", "음식종류", "설명"]
)

# (4) 식당-유형 매핑
type_of_restaurant_data = []
for resid in range(1, NUM_RESTAURANTS + 1):
    how_many = np.random.choice([1, 2], p=[0.7, 0.3])
    chosen = random.sample(range(1, len(korean_food_types) + 1), how_many)
    for c in chosen:
        type_of_restaurant_data.append([resid, c])
type_of_restaurant_df = pd.DataFrame(type_of_restaurant_data, columns=["식당ID", "유형ID"])

# (5) 방문기록 (자연편향)
monthly_visit_plan = {m: random.randint(180, 520) for m in range(1, 13)}
monthly_spending_range = {
    1: (10, 25),  2: (15, 30),  3: (25, 35),  4: (5, 15),
    5: (10, 22),  6: (13, 28),  7: (8, 18),   8: (16, 24),
    9: (14, 30), 10: (5, 20),  11: (20, 34), 12: (9, 21),
}

visits_data = []
for month, count in monthly_visit_plan.items():
    first_day = datetime(START_YEAR, month, 1)
    last_day = (first_day.replace(month=month % 12 + 1, day=1) - timedelta(days=1)) if month < 12 else datetime(START_YEAR, 12, 31)
    date_range = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]
    min_spent, max_spent = monthly_spending_range[month]

    for _ in range(count):
        student_id = random.randint(1, NUM_STUDENTS)
        restaurant_id = random.randint(1, NUM_RESTAURANTS)
        visit_date = random.choice(date_range)
        dt = visit_date.replace(hour=random.randint(11, 20), minute=random.randint(0, 59), second=random.randint(0, 59))
        spent = round(random.uniform(min_spent, max_spent), 2)
        visits_data.append([student_id, restaurant_id, dt.strftime("%Y-%m-%d %H:%M:%S"), spent])

visits_df = pd.DataFrame(visits_data, columns=["학생ID", "식당ID", "방문시간", "지출금액"])

# (6) 저장 및 압축
output_dir = "/mnt/data/최종_자연편향_데이터"
os.makedirs(output_dir, exist_ok=True)

students_df.to_csv(f"{output_dir}/학생정보.csv", index=False)
restaurants_df.to_csv(f"{output_dir}/식당정보.csv", index=False)
rest_types_df.to_csv(f"{output_dir}/식당유형.csv", index=False)
type_of_restaurant_df.to_csv(f"{output_dir}/식당_유형_매핑.csv", index=False)
visits_df.to_csv(f"{output_dir}/방문기록.csv", index=False)

final_zip_path = "/mnt/data/한글_식당_데이터셋_최종자연편향.zip"
with zipfile.ZipFile(final_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for file in os.listdir(output_dir):
        zipf.write(os.path.join(output_dir, file), arcname=file)

final_zip_path
