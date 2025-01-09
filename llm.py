from langchain_openai import ChatOpenAI
from constants import OPENAI_API_KEY
llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY, temperature=0.1)
