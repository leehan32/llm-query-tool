import os
import constants
from getDB import getDBEngine
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
import streamlit as st
from llm import llm
from Tools import generate_chart_ideas, write_query, execute_query, generate_chart_data, analyze_query_result
import pandas as pd
# Matplotlib 관련 import 제거
# import matplotlib.pyplot as plt
# import matplotlib.font_manager as fm
# import platform
from datetime import datetime

# 한글 폰트 및 스타일 설정 함수 제거
# def set_korean_font(): ...
# def set_chart_style(): ...

def streamlit_dashboard():
    # 앱 시작 시 폰트 및 스타일 설정 호출 제거
    # set_korean_font()
    
    # Initialize session state for visibility
    if 'show_confirmation' not in st.session_state:
        st.session_state.show_confirmation = False
        st.session_state.show_confirmation2 = False
        st.session_state.show_cancel = False
        st.session_state.show_query = False
        st.session_state.chart_ideas = []
        st.session_state.charts = []
        st.session_state.db_query = ""
        st.session_state.db_response = ""
        st.session_state.database_url = ""
        st.session_state.selected_chart_types = []
        st.session_state.df_data = None
        st.session_state.query_status = ""
        st.session_state.query_analysis = ""
    st.title("LLM Query Tool")

    
    # Collect business information
    business_info = st.text_area("💡 Please provide some information about your business:")

    # Collect database URL
    st.session_state.database_url = st.text_input("🔗 Enter your database URL:")
    
    # 시각화 유형 선택 옵션 추가
    chart_type_options = ["Bar chart", "Line chart", "Area chart", "Table"]
    selected_chart_types = st.multiselect("📊 Select chart types you want to generate:", 
                                         options=chart_type_options,
                                         default=["Bar chart", "Line chart", "Area chart"])
    st.session_state.selected_chart_types = selected_chart_types

    def generate_chart(chart_data, chart_type):
        # 스타일 설정 호출 제거
        # set_chart_style()
        
        x_axis_values = chart_data["x_axis_values"]
        y_axis_values = chart_data["y_axis_values"]
        columns = chart_data["columns"]

        # error handling
        if len(y_axis_values) == 0:
            y_axis_values.append([])

        # 데이터프레임 만들기 (Streamlit 기본 차트용)
        cdata = pd.DataFrame({}, index=x_axis_values)
        for index, column in enumerate(columns):
            # 배열 길이 확인 및 조정
            y_values = y_axis_values[index][:] if index < len(y_axis_values) else []
            # 길이가 짧을 경우 0으로 채우기
            while len(y_values) < len(x_axis_values):
                y_values.append(0)
            cdata[column] = y_values
            
        # # x축 값이 없으면 빈 데이터프레임 생성 (Streamlit은 index 기반으로 잘 처리하므로 불필요)
        # if not x_axis_values:
        #      cdata = pd.DataFrame(data_dict)
        # else:
        #      cdata = pd.DataFrame(data_dict, index=x_axis_values)

        # Streamlit 기본 차트로 복원
        if chart_type == "Table":
            st.table(cdata)
        # Matplotlib 코드 제거
        # else:
        #     # matplotlib로 차트 생성
        #     fig, ax = plt.subplots(figsize=(12, 6))
            
        #     # 차트 타입에 따라 그래프 생성
        elif chart_type == "Bar chart":
            # df.plot(kind='bar', ax=ax)
            st.bar_chart(cdata, use_container_width=True)
        elif chart_type == "Line chart":
            # df.plot(kind='line', ax=ax)
            st.line_chart(cdata, use_container_width=True)
        elif chart_type == "Area chart":
            # df.plot(kind='area', ax=ax)
            st.area_chart(cdata, use_container_width=True)
                
            # # x축 레이블 가로 표시 (Matplotlib 옵션 제거)
            # plt.xticks(rotation=0)
            
            # # 제목 설정 (Matplotlib 옵션 제거)
            # plt.title(chart_data["title"])
            # plt.tight_layout()
            
            # # Matplotlib 차트 출력 (제거)
            # st.pyplot(fig)
    
    def handle_yes_click():
        st.session_state.show_confirmation = False
        st.session_state.show_query = True

    def handle_no_click():
        st.session_state.show_confirmation = False
        st.session_state.show_cancel = True
        
    def reset_results():
        # 이전 결과 초기화
        st.session_state.charts = []
        st.session_state.chart_ideas = []
        st.session_state.db_query = ""
        st.session_state.db_response = ""
        st.session_state.show_query = False
        st.session_state.show_confirmation = False
        st.session_state.show_cancel = False
        st.session_state.query_status = ""
        st.session_state.query_analysis = ""

    if st.button("Submit"):
        # 이전 결과 초기화
        reset_results()
        
        if not st.session_state.selected_chart_types:
            st.error("최소한 하나 이상의 차트 유형을 선택해주세요.")
        else:
            try:
                with st.spinner("데이터베이스 정보 분석 중..."):
                    db = getDBEngine(st.session_state.database_url)
                    table_info = db.get_table_info()
                    chart_ideas = generate_chart_ideas(table_info, business_info, st.session_state.selected_chart_types)
                    st.session_state.chart_ideas = chart_ideas
                    st.subheader("다음 차트를 생성합니다 👇", divider=True)
                    st.code(chart_ideas[0]["info"])
                    st.session_state.show_confirmation = True
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")
                st.info("데이터베이스 연결 URL을 확인하고 다시 시도해주세요.")
    
    if st.session_state.show_cancel:
        st.write("Chart generation canceled.")

    if st.session_state.show_confirmation:
        st.write("위 차트를 생성하시겠습니까?")
        col1, col2, col3 = st.columns([1, 1, 10])
        with col1:
            st.button("예", key="yes_button", on_click=handle_yes_click)
        with col2:
            st.button("아니오", key="no_button", on_click=handle_no_click)
    
    if st.session_state.show_query:
        with st.spinner("📈 차트 데이터 생성 중..."):
            try:
                # 하나의 질문에 대해 데이터 가져오기
                idea = st.session_state.chart_ideas[0]
                
                # SQL 쿼리 생성
                with st.spinner("SQL 쿼리 생성 중..."):
                    query = write_query(idea["question"], st.session_state.database_url)
                    st.session_state.db_query = query
                
                # 쿼리 실행
                with st.spinner("쿼리 실행 중..."):
                    response = execute_query(query, st.session_state.database_url)
                    
                    # 쿼리 실행 상태 확인
                    if response["status"] == "success":
                        st.session_state.db_response = response["result"]
                        st.session_state.query_status = "success"
                    elif response["status"] == "corrected":
                        st.session_state.db_response = response["result"]
                        st.session_state.query_status = "corrected"
                        st.session_state.corrected_query = response["corrected_query"]
                        st.session_state.original_error = response["original_error"]
                    else:
                        st.error("쿼리 실행 중 오류가 발생했습니다.")
                        st.code(response["result"])
                        st.session_state.query_status = "error"
                        st.stop()
                
                # 쿼리 결과 분석
                with st.spinner("결과 분석 중..."):
                    analysis = analyze_query_result(idea["question"], query, response["result"])
                    st.session_state.query_analysis = analysis
                
                # 차트 데이터 생성
                with st.spinner("차트 데이터 생성 중..."):
                    chart_data = generate_chart_data(response["result"], idea["question"], query)
                    
                    # 선택한 모든 차트 유형에 대해 동일한 데이터를 사용하여 차트 생성
                    st.session_state.charts = []  # 기존 차트 초기화
                    for chart_type in st.session_state.selected_chart_types:
                        # 차트 타입만 변경하여 새로운 차트 데이터 생성
                        chart_data_copy = chart_data.copy()
                        chart_data_copy["chart_type"] = chart_type
                        st.session_state.charts.append(chart_data_copy)
            except Exception as e:
                st.error(f"차트 생성 중 오류 발생: {str(e)}")
                st.stop()

    if len(st.session_state.charts) > 0:
        st.subheader(st.session_state.charts[0]["title"], divider=True)
        
        # 차트 정보 및 인사이트 표시 (한 번만)
        st.markdown(':blue[💡 차트 정보]')
        st.write(st.session_state.chart_ideas[0]["info"])
        st.markdown(':blue[📊 차트 분석]')
        st.write(st.session_state.charts[0]["insights"])
        
        # 로그 정보 표시 (한 번만)
        with st.expander("Show Logs"):
            st.write("Database Query 👇")
            st.code(st.session_state.db_query)
            
            # 쿼리가 수정된 경우 표시
            if st.session_state.query_status == "corrected":
                st.warning(f"원래 쿼리에 오류가 있어 수정되었습니다: {st.session_state.original_error}")
                st.write("수정된 쿼리 👇")
                st.code(st.session_state.corrected_query)
            
            st.write("Database Response 👇")
            st.code(st.session_state.db_response)
            
            # 쿼리 결과 분석 표시
            if st.session_state.query_analysis:
                st.write("쿼리 결과 분석 👇")
                st.info(st.session_state.query_analysis)
        
        # 선택한 모든 차트 유형 표시
        for i, chart_data in enumerate(st.session_state.charts):
            with st.container(border=True):
                st.subheader(f"{chart_data['chart_type']} 시각화")
                generate_chart(chart_data, chart_data["chart_type"])

if __name__ == "__main__":
    # Openai key setup
    openai_key = constants.OPENAI_API_KEY
    os.environ['OPENAI_API_KEY'] = openai_key

    streamlit_dashboard()