import json
import requests
from gpt_analyzer import GPTAnalyzer

class CodeExtractor:
    def __init__(self):
        self.gpt_analyzer = GPTAnalyzer()

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
        
        self._save_to_file(coding_answers, analysis_prompt)
        return coding_answers

    def _extract_answer(self, question):
        student_questions = question.get('student_questions', {})
        answer = student_questions.get('answer')
        
        if answer:
            try:
                answer_data = json.loads(answer)
                if isinstance(answer_data.get('answer'), list):  # SQL format
                    for file in answer_data['answer']:
                        return {
                            'language': answer_data.get('language_name', 'Unknown'),
                            'filename': file.get('filename', ''),
                            'content': file.get('content', '')
                        }
                else:  # C# format
                    return {
                        'language': answer_data.get('language_name', 'Unknown'),
                        'filename': 'main.cs',
                        'content': answer_data.get('answer', '')
                    }
            except json.JSONDecodeError:
                return None
        return None

    def _save_to_file(self, coding_answers, analysis_prompt):
        with open('cod.txt', 'w', encoding='utf-8') as f:
            for i, answer in enumerate(coding_answers, 1):
                f.write(f"\nCoding Question {i}:\n")
                f.write(f"Language: {answer['language']}\n")
                f.write(f"File: {answer['filename']}\n")
                f.write("Content:\n")
                f.write(answer['content'])
                f.write("\n\nAnalysis Report:\n")
                analysis = self.gpt_analyzer.analyze_code(answer['content'], analysis_prompt)
                f.write(analysis)
                f.write("\n" + "-"*50 + "\n")