from typing_extensions import Annotated, TypedDict
from prompt import prompt_template
from getDB import getDBEngine
from llm import llm
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
import json

class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]

def generate_chart_ideas(table_info, business_info):
    response = llm.invoke(f"""
    You are an expert analyst. Your job is to create 3 different chart ideas from the given database information.
    
    You have given a business database and you will also be given some information about business and database. Based on that information you need to decide what type of database will be better for that business to show in dashboard.
                          
    You can generate charts from the following chart type list:
    - Bar chart
    - Line chart
    - Area chart
                          
    You have to generate a 20-25 words of a prompt to generate a specific chart which will be passed to the LLM model which will take your question and generate those charts. Make sure your prompt is easy to understand.

    Your final response MUST BE an array of objects where each object have the following fields:
    question: The prompt for LLM model to generate a relevant chart based on given business and database info 
    info: Tell what you are going to generate and why. (Your sentence should start like "A <chart_type> to show <what_you_are_showing> because it helps...")
    type: Chart type from the above 3 types
                          
    Here is how a sample question prompt looks like
    ---
    Generate a line chart to show the count of users with Basic plan based on their creation date
    ---
                          
    Here is the database information
    ---
    {table_info}
    ---

    Here is some information about business and database
    ---
    {business_info}
    ---

    NOTE: ONLY RESPOND WITH ARRAY OF OBJECTS WITHOUT MARKDOWN ELEMENTS AND MAKE SURE IT IS A VALID JSON
    """)
    responseJson = json.loads(response.content)
    return responseJson

def write_query(question, database_url):
    """Generate SQL query to fetch information."""
    db = getDBEngine(database_url)
    table_info = db.get_table_info()
    prompt = prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 20,
            "table_info": table_info,
            "input": question,
        }
    )
    structured_llm = llm.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)
    return result["query"]

def execute_query(query, database_url):
    """Execute SQL query."""
    db = getDBEngine(database_url)
    execute_query_tool = QuerySQLDataBaseTool(db=db)
    return {"result": execute_query_tool.invoke(query)}

def generate_chart_data(database_response, question, database_query):
    response = llm.invoke(f"""
    You are an expert data analyst. Your job is to create a data for given chart type. You will be given a database data along with a query which was used to get that data. You will also be given the question which explains what user want to plot on a chart along with the chart type. You need to get the database response and format it in the way that it can be plot on chart.
                          
    You can generate charts from the following chart type list:
    - Bar chart
    - Line chart
    - Area chart
                          
    Your final response MUST BE an object which have the following fields:
    title: A short title for the chart
    columns: an array of string where each element shows the name of the column of a dataframe. If there is only a single line in a line chart or a single bar in bar chart then there will be only 1 element in this array. If there are multiple lines in a line chart or multiple areas in area chart then there will be more than 1 elements in this array and each element will be the name of that column.
    y_axis_values: A 2D array of elements which will contain the y-axis data for each column. Each nested array will contain the y-axis data for that column and must have same length as x_axis_values array.
    x_axis_values: A 1D array of elements which will contain the x-axis data for each columns.
    chart_type: The type of chart from the above type list (The text must be same as the text in type list)
    insights: Some insights about the data which you got which can summarize the chart data in 50-100 words with proper line breaks
                          
    For example, we have a line chart which shows count of users for each month then the data will look like this:
    ---
    title: Users in last year
    columns: ["Users"]
    y_axis_data: [[12,3,4,... and so on for all months]]
    x_axis_data: [Jan,feb,mar,... and so on]
    chart_type: Line chart
    insights: Chart summary here
    ---
                          
    Here is the database query
    ---
    {database_query}
    ---

    Here is the database response for the given query
    ---
    {database_response}
    ---

    Here is the chart for which you need to generate the data
    ---
    {question}
    ---

    Make sure that the length of each nested array in y_axis_values is same as the length of x_axis_values array otherwise the code will break. You can put 0 to fill any array in y_axis_values to make it same length.

    NOTE: ONLY RESPOND WITH OBJECT WITHOUT MARKDOWN ELEMENTS AND MAKE SURE IT IS A VALID JSON
    """)
    responseJson = json.loads(response.content)
    return responseJson
