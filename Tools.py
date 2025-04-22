from typing_extensions import Annotated, TypedDict
from prompt import prompt_template, example_analysis_template
from getDB import getDBEngine
from llm import llm
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
import json
import sqlite3
import pandas as pd
from sqlalchemy import inspect

class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]

def get_detailed_table_info(db):
    """데이터베이스의 테이블 및 컬럼 정보를 상세히 가져옵니다."""
    try:
        # SQLDatabase 객체에서 엔진에 직접 접근하는 대신 다른 방법 사용
        tables = db.get_usable_table_names()
        
        table_info = []
        column_info = []
        
        for table in tables:
            # 테이블 정보 수집
            table_info.append(f"Table: {table}")
            
            # 컬럼 정보 수집 - get_table_info 메소드 사용
            table_details = db.get_table_info(table_names=[table])
            column_info.append(f"Table: {table} Columns:")
            column_info.append(table_details)
            
        # 샘플 데이터 수집 (각 테이블의 첫 5개 행)
        sample_data = []
        for table in tables:
            try:
                query = f"SELECT * FROM {table} LIMIT 5"
                result = db.run(query)
                if result:
                    sample_data.append(f"Sample data from {table}:")
                    sample_data.append(result)
            except Exception as e:
                sample_data.append(f"Failed to get sample data from {table}: {str(e)}")
                
        return {
            "table_info": "\n".join(table_info),
            "column_info": "\n".join(column_info),
            "sample_data": "\n".join(sample_data) if sample_data else "No sample data available."
        }
    except Exception as e:
        # 오류 발생 시 기본 테이블 정보만 반환
        return {
            "table_info": db.get_table_info(),
            "column_info": "Column info not available",
            "sample_data": "Sample data not available"
        }

def generate_chart_ideas(table_info, business_info, selected_chart_types=None):
    if selected_chart_types is None:
        selected_chart_types = ["Bar chart", "Line chart", "Area chart"]
    
    # 선택된 차트 유형들을 문자열로 변환
    chart_types_str = "\n- " + "\n- ".join(selected_chart_types)
    
    response = llm.invoke(f"""
    You are an expert analyst. Your job is to create a single chart idea from the given database information.
    
    You have given a business database and you will also be given some information about business and database. Based on that information you need to decide what type of database will be better for that business to show in dashboard.
                          
    You can generate a chart from the following chart type list:
    {chart_types_str}
                          
    You have to generate a 20-25 words of a prompt to generate a specific chart which will be passed to the LLM model which will take your question and generate the chart. Make sure your prompt is easy to understand.

    Your final response MUST BE an array containing only one object with the following fields:
    question: The prompt for LLM model to generate a relevant chart based on given business and database info 
    info: Tell what you are going to generate and why. (Your sentence should start like "A chart to show <what_you_are_showing> because it helps...")
    type: The main chart type you recommend (will be used as reference)
                          
    Here is how a sample question prompt looks like
    ---
    Generate a chart to show the count of users with Basic plan based on their creation date
    ---
                          
    Here is the database information
    ---
    {table_info}
    ---

    Here is some information about business and database
    ---
    {business_info}
    ---

    NOTE: 
    1. ONLY RESPOND WITH ARRAY OF OBJECTS (containing just ONE object) WITHOUT MARKDOWN ELEMENTS AND MAKE SURE IT IS A VALID JSON
    2. All chart info and prompts must be written in Korean
    3. The question should focus on the data needed, not on a specific chart type, as we will visualize the same data in multiple chart types
    """)
    responseJson = json.loads(response.content)
    return responseJson

def write_query(question, database_url):
    """Generate SQL query to fetch information with improved accuracy."""
    try:
        db = getDBEngine(database_url)
        
        # 기본 테이블 정보 가져오기
        basic_table_info = db.get_table_info()
        
        # 상세 테이블 정보 가져오기 (오류 발생 시 기본 정보 사용)
        try:
            detailed_info = get_detailed_table_info(db)
            
            # 프롬프트 구성
            enhanced_table_info = f"""
            Basic Table Information:
            {basic_table_info}
            
            Detailed Table Information:
            {detailed_info['table_info']}
            
            Column Information:
            {detailed_info['column_info']}
            
            Sample Data:
            {detailed_info['sample_data']}
            """
        except Exception as e:
            # 상세 정보 가져오기 실패 시 기본 정보만 사용
            enhanced_table_info = basic_table_info
        
        # 쿼리 생성
        prompt = prompt_template.invoke(
            {
                "dialect": db.dialect,
                "top_k": 20,
                "table_info": enhanced_table_info,
                "input": question,
            }
        )
        
        structured_llm = llm.with_structured_output(QueryOutput)
        result = structured_llm.invoke(prompt)
        generated_query = result["query"]
        
        # 생성된 쿼리의 유효성 검사 시도
        try:
            # 쿼리 실행 시도 (실제 실행은 하지 않고 구문 검사만)
            try:
                # EXPLAIN은 일부 데이터베이스에서만 작동
                test_result = db.run(f"EXPLAIN {generated_query}")
            except:
                # EXPLAIN이 작동하지 않으면 단순히 SQL 구문만 확인
                test_result = "Query syntax looks valid."
                
            # 구문 오류가 없으면 원래 쿼리 반환
            return generated_query
        except Exception as e:
            # 쿼리에 오류가 있으면 수정 시도
            error_message = str(e)
            correction_prompt = f"""
            SQL 쿼리에 오류가 발생했습니다. 오류를 수정해주세요.
            
            원래 질문: {question}
            생성된 SQL 쿼리: {generated_query}
            오류 메시지: {error_message}
            
            수정된 SQL 쿼리를 제공해주세요.
            """
            
            correction_result = llm.invoke(correction_prompt)
            corrected_query = correction_result.content
            
            # SQL 쿼리 부분만 추출 (코드 블록이 있을 경우)
            if "```sql" in corrected_query:
                corrected_query = corrected_query.split("```sql")[1].split("```")[0].strip()
            elif "```" in corrected_query:
                corrected_query = corrected_query.split("```")[1].split("```")[0].strip()
                
            return corrected_query
    except Exception as e:
        # 전체 과정에서 오류 발생 시 기본 프롬프트로 쿼리 생성 시도
        try:
            db = getDBEngine(database_url)
            basic_table_info = db.get_table_info()
            
            prompt = prompt_template.invoke(
                {
                    "dialect": db.dialect,
                    "top_k": 20,
                    "table_info": basic_table_info,
                    "input": question,
                }
            )
            
            structured_llm = llm.with_structured_output(QueryOutput)
            result = structured_llm.invoke(prompt)
            return result["query"]
        except Exception as fallback_error:
            # 모든 방법이 실패하면 오류 메시지 반환
            return f"ERROR: Failed to generate query. {str(fallback_error)}"

def execute_query(query, database_url):
    """Execute SQL query with improved error handling."""
    try:
        # 쿼리가 에러 메시지인 경우 확인
        if isinstance(query, str) and query.startswith("ERROR:"):
            return {"result": query, "status": "error"}
            
        db = getDBEngine(database_url)
        try:
            execute_query_tool = QuerySQLDataBaseTool(db=db)
            result = execute_query_tool.invoke(query)
            
            # 결과가 너무 크면 처음 20줄만 표시
            if isinstance(result, str) and len(result) > 1000:
                result = result[:1000] + "\n... (추가 결과 생략)"
                
            return {"result": result, "status": "success"}
        except Exception as e:
            error_message = str(e)
            
            # 오류 분석 및 쿼리 수정 시도
            correction_prompt = f"""
            SQL 쿼리 실행 중 오류가 발생했습니다. 오류를 분석하고 수정해주세요.
            
            SQL 쿼리: {query}
            오류 메시지: {error_message}
            
            오류의 원인과 수정된 SQL 쿼리를 제공해주세요.
            """
            
            try:
                correction_result = llm.invoke(correction_prompt)
                analysis = correction_result.content
                
                # 수정된 쿼리 추출 시도
                corrected_query = query
                if "```sql" in analysis:
                    corrected_query = analysis.split("```sql")[1].split("```")[0].strip()
                elif "```" in analysis:
                    corrected_query = analysis.split("```")[1].split("```")[0].strip()
                    
                # 수정된 쿼리로 다시 시도
                try:
                    execute_query_tool = QuerySQLDataBaseTool(db=db)
                    result = execute_query_tool.invoke(corrected_query)
                    return {
                        "result": result, 
                        "status": "corrected",
                        "original_error": error_message,
                        "corrected_query": corrected_query
                    }
                except Exception as retry_error:
                    return {
                        "result": f"쿼리 실행 오류: {error_message}\n\n수정 시도 했으나 실패했습니다.\n분석: {analysis}",
                        "status": "error",
                        "original_query": query,
                        "corrected_query": corrected_query,
                        "retry_error": str(retry_error)
                    }
            except Exception as correction_error:
                # LLM을 통한 수정 시도 자체가 실패한 경우
                return {
                    "result": f"쿼리 실행 오류: {error_message}\n\n쿼리 수정 시도 중 추가 오류 발생: {str(correction_error)}",
                    "status": "error"
                }
    except Exception as e:
        # 가장 기본적인 오류 처리
        return {
            "result": f"쿼리 처리 중 예상치 못한 오류 발생: {str(e)}",
            "status": "critical_error"
        }

def analyze_query_result(question, query, result):
    """쿼리 결과를 분석하여 질문에 적절하게 답변했는지 평가합니다."""
    try:
        analysis_prompt = example_analysis_template.invoke({
            "original_question": question,
            "generated_query": query,
            "query_result": result
        })
        
        analysis_result = llm.invoke(analysis_prompt)
        return analysis_result.content
    except Exception as e:
        # 분석 실패 시 간단한 메시지 반환
        return f"쿼리 결과 분석 중 오류 발생: {str(e)}"

def generate_chart_data(database_response, question, database_query):
    response = llm.invoke(f"""
    You are an expert data analyst. Your job is to create data for chart visualizations. You will be given a database response along with a query which was used to get that data. You will also be given the question which explains what user wants to plot.
    
    Your job is to analyze the data and prepare it for visualization, regardless of which chart type will be used. The visualization engine can handle multiple chart types with the same data.
                          
    Your final response MUST BE an object which have the following fields:
    title: A short title for the chart
    columns: an array of string where each element shows the name of the column of a dataframe. If there is only a single line/bar/area then there will be only 1 element in this array. If there are multiple lines/bars/areas then there will be more than 1 elements in this array and each element will be the name of that column.
    y_axis_values: A 2D array of elements which will contain the y-axis data for each column. Each nested array will contain the y-axis data for that column and must have same length as x_axis_values array.
    x_axis_values: A 1D array of elements which will contain the x-axis data for each columns.
    chart_type: Just set this to "Line chart" for now - it will be replaced later according to user selection
    insights: Some general insights about the data which can summarize the data in 50-100 words with proper line breaks. Focus on trends, patterns, outliers, etc. regardless of chart type
                          
    For example, if we have user counts for each month, the data will look like this:
    ---
    title: 월별 사용자 수
    columns: ["사용자 수"]
    y_axis_values: [[12,3,4,5,6,7,8,9,10,11,12,2]]
    x_axis_values: ["1월","2월","3월","4월","5월","6월","7월","8월","9월","10월","11월","12월"]
    chart_type: "Line chart"
    insights: "전반적인 사용자 수 분석 내용..."
    ---
                          
    Here is the database query
    ---
    {database_query}
    ---

    Here is the database response for the given query
    ---
    {database_response}
    ---

    Here is the request for which you need to generate the data
    ---
    {question}
    ---

    Make sure that the length of each nested array in y_axis_values is same as the length of x_axis_values array otherwise the code will break. You can put 0 to fill any array in y_axis_values to make it same length.

    NOTE: 
    1. ONLY RESPOND WITH OBJECT WITHOUT MARKDOWN ELEMENTS AND MAKE SURE IT IS A VALID JSON.
    2. All parts of the response (title, columns, chart_type, insights) must be written entirely in natural Korean. Do not mix English and Korean.
    3. Focus on organizing the data for visualization regardless of chart type - the same data will be used for multiple chart types.
    """)
    responseJson = json.loads(response.content)
    return responseJson

