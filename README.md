
# 📊 자연어 기반 동적 대시보드 생성기 (LLM + Streamlit)

이 프로젝트는 **LLM(Large Language Model)**을 활용해 사용자의 자연어 질문으로부터  
자동으로 SQL 쿼리를 생성하고, 실제 데이터베이스에 실행하여 시각화 차트를 생성하는  
**Streamlit 기반의 데이터 분석 대시보드 생성 도구**입니다.

- 🧠 **LLM 기반 질의 이해 + SQL 생성**
- 🗄️ **PostgreSQL (Supabase 포함) 실시간 연결**
- 📈 **Streamlit을 통한 웹 기반 차트 시각화**
- 🛠️ **LangChain을 통한 쿼리 생성 및 오류 보정**
- ✅ **한국어 질문  지원 + 분석 피드백 자동 제공**

---

## 🔁 주요 동작 흐름

1. 사용자의 자연어 질문 입력
2. DB 구조/샘플 데이터 기반 차트 아이디어 생성
3. SQL 쿼리 생성 (오류 시 보정 포함)
4. DB에 쿼리 실행
5. 결과를 차트 포맷으로 변환 후 시각화
6. 쿼리 결과 분석 및 피드백 표시

---

## 📦 프로젝트 구조

```
📁 프로젝트 루트
├── index.py           # Streamlit 기반 UI 흐름 전체 담당
├── Tools.py           # 쿼리 생성, 실행, 오류 보정, 분석 등 핵심 로직
├── prompt.py          # LLM 프롬프트 템플릿 정의
├── getDB.py           # DB 연결 엔진 정의 (SQLAlchemy 기반)
├── constants.py       # API Key 저장 파일 (git에는 포함시키지 마세요)
├── requirements.txt   # 설치할 의존성 패키지 목록
```

---

## 🚀 실행 방법

### 1. 사전 준비
- Python 3.9+ 환경
- OpenAI API 키
- PostgreSQL DB (Supabase도 가능)

### 2. `constants.py` 작성
```python
OPENAI_API_KEY = "sk-..."
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 실행
```bash
streamlit run index.py
```

---

## 📊 차트 시각화 기능

- 사용자가 직접 원하는 차트 타입 선택 (`Bar`, `Line`, `Area`)
-  <img src="https://github.com/user-attachments/assets/236a3a80-a186-4e3b-8be7-fee06980f5ea" width="500">
- LLM이 자동으로 생성한 차트를 타입별로 반복 렌더링
- 각 차트에 대한 설명 및 분석 자동 출력
- <img src="https://github.com/user-attachments/assets/ce9fe4d1-5e8b-4c7a-8776-f4117e9abe64" width="500">  
- 쿼리, 결과, 분석 로그 확인 가능
- <img src="https://github.com/user-attachments/assets/cfe741db-a69e-46bf-aee1-51191e2215eb" width="500">



---

## 🔐 보안 주의사항 (Streamlit Cloud 배포 시)

- GitHub에 API 키는 절대 업로드하지 마세요
- `st.secrets`를 활용하거나 `constants.py`는 `.gitignore`에 추가하세요
- 민감 API나 DB에는 인증 또는 요청 제한 기능을 추가하는 것을 권장합니다

---

## 📌 향후 개선 아이디어

- WebSocket 기반 실시간 응답 구조
- 사용자 세션 기반 로그 기록
- 차트 다운로드 기능 (`.png`, `.csv`)
- GKE + HTTPS 기반 외부 접근 완성


## 🙋‍♂️ 기여자

이 프로젝트는 LLM 기반의 자연어 데이터 분석 도구를 직접 설계/구현한 실험적 데모입니다.
