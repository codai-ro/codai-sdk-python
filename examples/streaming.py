"""Streaming chat completion.

    CODAI_API_KEY=sk_... python examples/streaming.py
"""
import os
import sys

from codai import Codai

client = Codai(api_key=os.environ["CODAI_API_KEY"])

for delta in client.chat_stream([{"role": "user", "content": "Write a haiku about Python."}]):
    sys.stdout.write(delta)
    sys.stdout.flush()
print()
