import os
import constants
from getDB import getDBEngine
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
import streamlit as st
from llm import llm
from Tools import generate_chart_ideas, write_query, execute_query, generate_chart_data
import pandas as pd

def streamlit_dashboard():
    # Initialize session state for visibility
    if 'show_confirmation' not in st.session_state:
        st.session_state.show_confirmation = False
        st.session_state.show_confirmation2 = False
        st.session_state.show_cancel = False
        st.session_state.show_query = False
        st.session_state.chart_ideas = []
        st.session_state.charts = []
        st.session_state.db_query = []
        st.session_state.db_response = []
        st.session_state.database_url = ""
    st.title("LLM Query Tool")

    
    # Collect business information
    business_info = st.text_area("💡 Please provide some information about your business:")

    # Collect database URL
    st.session_state.database_url = st.text_input("🔗 Enter your database URL:")

    def generate_chart(chart_data):
        x_axis_values = chart_data["x_axis_values"]
        y_axis_values = chart_data["y_axis_values"]
        columns = chart_data["columns"]
        chart_type = chart_data["chart_type"]

        # error handling
        if len(y_axis_values) == 0:
            y_axis_values.append([])

        cdata = pd.DataFrame({
        }, index=x_axis_values)
        for index, column in enumerate(columns):
            # To make all arrays same length
            if len(y_axis_values[index]) != len(x_axis_values):
                rem = len(x_axis_values) - len(y_axis_values[index])
                while rem:
                    y_axis_values[index].append(0)
                    rem = rem - 1
            cdata[column] = y_axis_values[index]

        if chart_type == "Bar chart":
            st.bar_chart(cdata)
        elif chart_type == "Line chart":
            st.line_chart(cdata)
        elif chart_type == "Area chart":
            st.area_chart(cdata)
    
    def handle_yes_click():
        st.session_state.show_confirmation = False
        st.session_state.show_query = True

    def handle_no_click():
        st.session_state.show_confirmation = False
        st.session_state.show_cancel = True

    if st.button("Submit"):
        db = getDBEngine(st.session_state.database_url)
        table_info = db.get_table_info()
        chart_ideas = generate_chart_ideas(table_info,business_info)
        st.session_state.chart_ideas = chart_ideas
        st.subheader("We are going to generate the following charts 👇", divider=True)
        for idea in chart_ideas:
            st.code(idea["info"])
        st.session_state.show_confirmation = True
    
    if st.session_state.show_cancel:
        st.write("Chart generation canceled.")

    if st.session_state.show_confirmation:
        st.write("Do you want to generate these charts?")
        col1, col2, col3 = st.columns([1, 1, 10])
        with col1:
            st.button("Yes", key="yes_button", on_click=handle_yes_click)
        with col2:
            st.button("No", key="no_button", on_click=handle_no_click)
    
    if st.session_state.show_query:
        st.write("📈 Generating charts...")
        for idea in st.session_state.chart_ideas:
            query = write_query(idea["question"],st.session_state.database_url)
            st.session_state.db_query.append(query)
            response = execute_query(query, st.session_state.database_url)
            st.session_state.db_response.append(response["result"])
            chart_data = generate_chart_data(response["result"],idea["question"],query)
            st.session_state.charts.append(chart_data)

    if len(st.session_state.charts) > 0:
        for i, chart_data in enumerate(st.session_state.charts):
            with st.container(border=True):
                st.subheader(chart_data["title"])
                generate_chart(chart_data)
                st.markdown(':blue[💡 Chart Info]')
                st.write(st.session_state.chart_ideas[i]["info"])
                st.markdown(':blue[📊 Chart Analysis]')
                st.write(chart_data["insights"])
                with st.expander("Show Logs"):
                    st.write("Database Query 👇")
                    st.code(st.session_state.db_query[i])
                    st.write("Database Response 👇")
                    st.code(st.session_state.db_response[i])

if __name__ == "__main__":
    # Openai key setup
    openai_key = constants.OPENAI_API_KEY
    os.environ['OPENAI_API_KEY'] = openai_key

    streamlit_dashboard()