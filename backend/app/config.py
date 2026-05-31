import os


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agentops.db")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "llama3.2:3b")

