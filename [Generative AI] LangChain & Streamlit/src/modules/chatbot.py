import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts.prompt import PromptTemplate
from langchain.callbacks import get_openai_callback

#fix Error: module 'langchain' has no attribute 'verbose'
import langchain
langchain.verbose = False

class Chatbot:

    def __init__(self, model_name, temperature, vectors):
        self.model_name = model_name
        self.temperature = temperature
        self.vectors = vectors

    qa_template = """
        Tu es un assistant IA serviable, au sein du promoteur immobilier français Kaufman & Broad. 
        L'utilisateur te donne un fichier dont le contenu est représenté par les éléments de contexte suivants, utilise-les pour répondre à la question à la fin.
        Si tu ne connais pas la réponse, dis simplement que tu ne sais pas. N'essaie PAS d'inventer une réponse.
        Si la question n'est pas liée au contexte, réponds poliment que tu es programmé pour ne répondre qu'aux questions liées au contexte.
        Utilise autant de détails que possible lorsque tu réponds.

        contexte: {context}
        =========
        question: {question}
        ======
        """

    QA_PROMPT = PromptTemplate(template=qa_template, input_variables=["context", "question"])

    def conversational_chat(self, query):
        """
        Start a conversational chat with a model via Langchain
        """
        llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)

        retriever = self.vectors.as_retriever()

        chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, verbose=True,
                                                      return_source_documents=True, max_tokens_limit=8192,
                                                      combine_docs_chain_kwargs={'prompt': self.QA_PROMPT})

        chain_input = {"question": query, "chat_history": st.session_state["history"]}
        result = chain(chain_input, return_only_outputs=True)

        st.session_state["history"].append((query, result["answer"]))
        #count_tokens_chain(chain, chain_input)
        return result["answer"]


def count_tokens_chain(chain, query):
    with get_openai_callback() as cb:
        result = chain.run(query)
        st.write(f'###### Tokens used in this conversation : {cb.total_tokens} tokens')
    return result 

    
    
