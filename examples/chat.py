"""Basic chat completion.

    CODAI_API_KEY=sk_... python examples/chat.py
"""
import os

from codai import Codai

client = Codai(api_key=os.environ["CODAI_API_KEY"])

result = client.chat([{"role": "user", "content": "Give me one tip for clean Python."}])

print(result.content)
print("routed to:", result.routed_to)
