"""Server-side agent run.

    CODAI_API_KEY=sk_... python examples/agent.py
"""
import os

from codai import Codai

client = Codai(api_key=os.environ["CODAI_API_KEY"])

run = client.agents_run(
    "Summarize the following text in 3 bullet points.",
    context="codai is an OpenAI-compatible AI gateway with smart routing.",
)

print(run.result)
