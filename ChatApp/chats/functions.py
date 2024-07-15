from langchain.chains import (
    create_history_aware_retriever,
    create_retrieval_chain,
)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.retrievers import (
    PineconeHybridSearchRetriever,
)
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from pinecone_text.sparse import BM25Encoder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_pinecone import PineconeVectorStore
from django.conf import settings
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from django.core.serializers.json import DjangoJSONEncoder

import nltk
#PATH = "../bm25_values.json"
#bm25_encoder = BM25Encoder().load(PATH)

def create_rag_pipeline():
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
    PINECONE_INDEX = 'fault-finding'
    EMBEDDINGS_MODEL = "text-embedding-ada-002"
    LLM = "gpt-3.5-turbo"
    load_dotenv()
    #nltk.download('stopwords')
    #pc = Pinecone()
    #index = pc.Index(PINECONE_INDEX)
    embeddings = OpenAIEmbeddings(model=EMBEDDINGS_MODEL)
    retriever = PineconeVectorStore(index_name=PINECONE_INDEX, embedding=embeddings,
                                    pinecone_api_key=PINECONE_API_KEY).as_retriever()
    model = ChatOpenAI(model=LLM, temperature=0)
    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        model, retriever, contextualize_q_prompt
    )

    qa_system_prompt = """"You are a chat application answering questions \
    about electrical installation fault finding and general electrical questions" \

    {context}"""
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(model, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return rag_chain


def generate_response(question, history):
    rag_chain = settings.RAG_CHAIN
    ai_response = rag_chain.invoke({"input": question, "chat_history": history})
    history.extend([HumanMessage(content=question), ai_response["answer"]])
    return ai_response


store = {}


# def get_session_history(session_id: str) -> BaseChatMessageHistory:
#     if session_id not in store:
#         store[session_id] = ChatMessageHistory()
#     return store[session_id]

class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, ChatMessageHistory):
            return obj.to_dict()  # Implement to_dict method in ChatMessageHistory
        return super().default(obj)

def gr(question, session_id, get_session_history):
    rag_chain = settings.RAG_CHAIN
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    response = conversational_rag_chain.invoke(
        {"input": question},
        config={
            "configurable": {"session_id": session_id}
        }
    )
    return response
