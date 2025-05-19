import os
import streamlit as st
from langchain_groq import ChatGroq


class GroqLLM:
    def __init__(self, user_controls_input=None, model=None, api_key=None):
        self.user_controls_input = user_controls_input
        self.model = model
        self.api_key = api_key
        
        
    def get_llm_model(self):
        try:
            if  self.user_controls_input:
                groq_api_key = self.user_controls_input['GROQ_API_KEY']
                selected_groq_model = self.user_controls_input['selected_groq_model']
                llm = ChatGroq(api_key=groq_api_key, model= selected_groq_model)
            else:
                llm = ChatGroq(api_key=self.api_key,model=self.model)
        
        except Exception as e:
            raise ValueError(f"Error occured with Exception : {e}")
        
        return llm