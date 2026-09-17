import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_API_URL")
model = os.getenv("OPENAI_MODEL")

print("API key :" , "Yes" if api_key else "No")
print("Base URL :" , base_url)
print("Model :" , model)

client = OpenAI(
    api_key=api_key ,
    base_url=base_url,
)

resp = client.chat.completions.create(
    model = model,
    messages = [
        {
            "role" : "user" ,
            "content" : "请回复：电商售后系统连接成功"
        }
    ]
)

print()
print(f"Response : {resp.choices[0].message.content}")