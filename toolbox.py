from toolbox_langchain import ToolboxClient
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI

# MCP Toolbox 서버 주소
client = ToolboxClient("http://localhost:5000")

# Toolset 로드 (tools.yaml에서 정의한 이름 사용)
tools = client.load_toolset("default")

# LLM 설정 (예: OpenAI)
llm = ChatOpenAI(model="gpt-4", temperature=0)

# LangChain Agent 초기화
agent = initialize_agent(
    tools,
    llm,
    agent_type="openai-tools",
    verbose=True,
)

# 실행
response = agent.run("example 테이블의 모든 행을 보여줘")
print(response)
