from openai import AzureOpenAI
from config import Config

class GPTAnalyzer:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )

    def analyze_code(self, code_content, analysis_prompt):
        try:
            response = self.client.chat.completions.create(
                model=Config.AZURE_OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a code reviewer. Provide a brief, focused analysis in 3 lines maximum, highlighting only critical issues."},
                    {"role": "user", "content": f"Based on these criteria: {analysis_prompt}\n\nAnalyze this code:\n{code_content}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error in GPT analysis: {str(e)}"