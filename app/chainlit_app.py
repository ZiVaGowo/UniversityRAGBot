import chainlit as cl

@cl.on_chat_start
async def start():
    await cl.Message(content="Привет! Я AI-ассистент.").send()

@cl.on_message
async def main(msg: cl.Message):
    await cl.Message(content=f"Ты сказал: {msg.content}").send()