# 한글 식당 방문 데이터셋 (자연편향 버전)

본 데이터셋은 식당 방문 기록을 기반으로 한 AI 분석 및 LLM 기반 자연어 질의 실험을 위해 설계된 한글 버전 데이터셋입니다.  
원본 데이터셋에서 다음과 같은 확장 및 편향 로직이 반영되어 있습니다.

---

## ✅ 데이터셋 구성

| 파일명 | 설명 |
|--------|------|
| `학생정보.csv` | 100명의 한글 이름 기반 학생 정보 |
| `식당정보.csv` | 10개의 한글 조합 식당 이름 및 평점 정보 |
| `식당유형.csv` | 피자, 한식 등 실생활 기반 8종의 음식 유형 |
| `식당_유형_매핑.csv` | 각 식당과 음식 유형 간 다대다 관계 |
| `방문기록.csv` | 2024년 1월 ~ 12월 동안 발생한 방문 기록 (총 4,600건 이상) |

---

## 🔧 주요 변경 및 편향 요소

- **학생 수**: 30명 → 100명으로 증가
- **방문 기간**: 2023년 1월 → 2024년 1월 ~ 12월로 확장
- **방문 수**: 월별 180~520건으로 다르게 설정 (자연스러운 분포)
- **지출 금액**: 각 월별로 범위를 다르게 지정 (예: 3월은 25~35, 4월은 5~15 등)
- **식당 이름**: `Restaurant_1` → `맛집`, `불마루` 등 한글 4글자 이내 조합
- **음식 유형**: Grill, Korean 등 → 피자, 분식, 초밥 등 실생활 기반 한글화
- **컬럼명**: 모든 컬럼명을 한글로 변경

---

## 📌 목적

- LLM 자연어 질의 응답 실험용
- 월별 매출/방문 분석 및 시계열 기반 인사이트 도출
- 한글 기반 데이터셋에 대한 SQL/AI 호환성 실험

---

## 📁 생성 파일

압축 파일명: `한글_식당_데이터셋_최종자연편향.zip`  
모든 `.csv` 파일은 UTF-8 인코딩으로 저장되어 있습니다.
"""

# 파일 저장
readme_path = "/mnt/data/README_한글식당자연편향.md"
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme_text.strip())

readme_path
