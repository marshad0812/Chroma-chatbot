import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

from langchain.document_loaders import DirectoryLoader
from langchain.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings
from langchain.indexes.vectorstore import VectorStoreIndexWrapper, \
    VectorstoreIndexCreator
from langchain.vectorstores import Chroma
from pydantic import BaseModel
import base64
import openai
from gtts import gTTS

model_id = "gpt-3.5-turbo"

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Data(BaseModel):
    message: str
    key: str


@app.post("/send_message")
async def send_message(message: Data):
    """this function will receive the message from Ui and send it to openai whisper ai and return the response"""
    try:
        audio_file = open("temp.mp3", "wb")
        decode_string = base64.b64decode(message.message)
        audio_file.write(decode_string)
        audio_file.close()
        file = open("temp.mp3", "rb")
        openai.api_key = message.key
        transcript = openai.Audio.translate("whisper-1", file)
        return {"message": transcript.get('text')}
    except openai.error.AuthenticationError:
        return {"message": "Incorrect API key provided in settings",
                "error": True}
    except openai.error.RateLimitError:
        return {"message": "API rate limit exceeded",
                "error": True}


class GPTData(BaseModel):
    message: str
    conversation: list
    key: str


@app.post("/get_result")
async def get_result(gpt: GPTData):
    """this function will  send the transcribed text  to openai gpt-3.5 turbo ai and return the response """
    try:
        # openai.api_key = "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"
        os.environ[
            "OPENAI_API_KEY"] = gpt.key
        print(gpt.conversation)
        PERSIST = False

        # query = None
        # if len(sys.argv) > 1:
        #     print("Using query from command line...\n")
        #     query = sys.argv[1]

        if PERSIST and os.path.exists("persist"):
            print("Reusing index...\n")
            vectorstore = Chroma(persist_directory="persist",
                                 embedding_function=OpenAIEmbeddings())
            index = VectorStoreIndexWrapper(vectorstore=vectorstore)
        else:
            print('else')
            # loader = TextLoader("data/data.txt") # Use this line if you only need data.txt
            loader = DirectoryLoader("data/")
            print('loader')
            if PERSIST:
                print("persist")
                index = VectorstoreIndexCreator(vectorstore_kwargs={
                    "persist_directory": "persist"}).from_loaders([loader])
            else:
                openai.api_key
                print('else 2')
                index = VectorstoreIndexCreator().from_loaders([loader])
                print("33333333")
        memory = ConversationBufferMemory(memory_key="chat_history",
                                          return_messages=True)

        chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(model="gpt-3.5-turbo"),
            retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1},memory=memory),
        )
        print('444444444')

        chat_history = [tuple(cht) for cht in gpt.conversation]

        result = chain({"question": gpt.message, "chat_history": chat_history})
        print(result, 'result')

        chat_history.append((gpt.message, result['answer']))
        print(chat_history)
        tts = gTTS(text=result['answer'], lang='en')
        tts.save("temp.mp3")
        with open("temp.mp3", "rb") as f:
            base64_bytes = base64.b64encode(f.read())
            base64_string = base64_bytes.decode('utf-8')
        return {"conversation": chat_history,
                "message": result['answer'],
                "voice": base64_string}
    except openai.error.AuthenticationError as e:
        return {"conversation": gpt.conversation,
                "message": "Incorrect API key provided in settings",
                "error": True}
    except openai.error.RateLimitError:
        return {"message": "API rate limit exceeded",
                "error": True}


uvicorn.run(app, host="0.0.0.0", port=8000)
