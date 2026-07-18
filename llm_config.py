from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
load_dotenv()

llm = ChatOpenAI(
    model="tencent/hy3:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.8,
    streaming=True
)
