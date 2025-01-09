from langchain_core.prompts import PromptTemplate
prompt_template = PromptTemplate.from_template("""
Given an input question, create a syntactically correct {dialect} query to run to help find the answer. Unless the user specifies in his question a specific number of examples they wish to obtain, always limit your query to at most {top_k} results. You can order the results by a relevant column to return the most interesting examples in the database.

Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.

Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.

Note: If you are generating a postgresql query and a table name or column name starts with a capital letter then wrap it with double quotes. For example if the table name is Users then in query it should be "Users". Similarly if a column name is UserID then in query it should be u."UserID" instead of u.UserID

Only use the following tables:
{table_info}

Question: {input}
""")