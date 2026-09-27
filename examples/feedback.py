"""Submit feedback on a completion.

    CODAI_API_KEY=sk_... python examples/feedback.py
"""
import os

from codai import Codai

client = Codai(api_key=os.environ["CODAI_API_KEY"])

result = client.chat([{"role": "user", "content": "Hello!"}])

if result.request_id:
    client.feedback(result.request_id, 1)  # 1 = up, -1 = down
    print("feedback submitted for", result.request_id)
