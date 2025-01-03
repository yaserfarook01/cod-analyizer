import json
import requests
from gpt_analyzer import GPTAnalyzer
from file_handler import FileHandler

class CodeExtractor:
    def __init__(self):
        self.gpt_analyzer = GPTAnalyzer()
        self.file_handler = FileHandler()

    def get_coding_answers(self, url, auth_token, analysis_prompt):
        try:
            test_id = url.split('testId=')[1]
            api_url = "https://api.examly.io/api/v2/test/student/resultanalysis"
            
            headers = {
                'accept': 'application/json, text/plain, */*',
                'authorization': auth_token,
                'content-type': 'application/json'
            }
            
            data = {
                "id": test_id
            }

            response = requests.post(api_url, headers=headers, json=data)
            if response.status_code == 200:
                response_data = response.json()
                coding_answers = self._process_response(response_data, analysis_prompt)
                return coding_answers, True
            else:
                return f"Error: Status code {response.status_code}", False
                
        except Exception as e:
            return f"Error: {str(e)}", False

    def _process_response(self, response_data, analysis_prompt):
        coding_answers = []
        
        for section in response_data.get('frozen_test_data', []):
            if section.get('name') == 'COD':
                questions = section.get('questions', [])
                
                for question in questions:
                    answer = self._extract_answer(question)
                    if answer:
                        coding_answers.append(answer)
        
        self.file_handler.save_analysis(coding_answers, analysis_prompt, self.gpt_analyzer)
        return coding_answers

    def _extract_answer(self, question):
        try:
            student_questions = question.get('student_questions', {})
            answer = student_questions.get('answer')
            
            if answer:
                answer_data = json.loads(answer)
                return {
                    'language': answer_data.get('language_name', 'Unknown'),
                    'filename': self._get_filename(answer_data.get('language_name', '')),
                    'content': answer_data.get('answer', ''),
                    'question_data': question
                }
        except json.JSONDecodeError:
            return None
        return None

    def _get_filename(self, language):
        extensions = {
            'Java': 'main.java',
            'Python': 'main.py',
            'C#': 'main.cs',
            'JavaScript': 'main.js',
            'SQL': 'query.sql'
        }
        return extensions.get(language, 'main.txt')
