import os
from google import genai

# client get api key from : environment variable `GEMINI_API_KEY`

class LLMGenerator:
    def __init__(self, api_key=None, model_name="gemini-3-flash-preview"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY daalo bhai!")
        self.client = genai.Client(api_key=api_key)
        self.model_name =model_name
        

    def generate_answer(self, query, context):

        prompt = f"""
                You are a helpful AI assistant.
                Answer the question strictly using the context below.
                If the answer is not present in the context, reply and say: "I don't have enough information from the uploaded PDF(s)."

                Context:
                {context}

                Question:
                {query}

                """

        response = self.client.models.generate_content(
                    model=self.model_name, 
                    contents=prompt
                    )
        
        return response.text
