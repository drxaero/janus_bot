import chainlit as cl
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_community.llms.ctransformers import CTransformers
from langchain_core.prompts import PromptTemplate


class StreamHandler(BaseCallbackHandler):
    """
    自己設計給 chainlit 用的 stream callback
    """

    def __init__(self):
        self.msg = cl.Message(content="")

    async def on_llm_new_token(self, token: str, **kwargs):
        await self.msg.stream_token(token)

    async def on_llm_end(self, response: str, **kwargs):
        await self.msg.send()
        self.msg = cl.Message(content="")


# Load quantized Llama 2
llm = CTransformers(
    model="TheBloke/Llama-2-7B-Chat-GGUF",
    model_file="llama-2-7b-chat.Q2_K.gguf",
    model_type="llama2",
    max_new_tokens=20,
)

llm_chain_variable = "llm_chain"
context_variable = "context"
instruction_variable = "instruction"

template = f"""
[INST] <<SYS>>
You are a helpful, respectful and honest assistant.
Always provide a concise answer and use the following Context:
{{{context_variable}}}
<</SYS>>
User:
{{{instruction_variable}}}[/INST]"""

prompt = PromptTemplate(template=template, input_variables=[context_variable, instruction_variable])


@cl.on_chat_start
def on_chat_start():
    memory = ConversationBufferMemory(memory_key=context_variable)
    llm_chain = LLMChain(prompt=prompt, llm=llm, verbose=False, memory=memory)
    cl.user_session.set(llm_chain_variable, llm_chain)


@cl.on_message
async def on_message(message: cl.Message):
    llm_chain = cl.user_session.get(llm_chain_variable)

    await llm_chain.ainvoke(
        message.content,
        config={"callbacks": [cl.AsyncLangchainCallbackHandler(), StreamHandler()]},
    )
