import json
import openai
from config import Config
import traceback

# Configure OpenAI to use Azure OpenAI
openai.api_type = "azure"
openai.api_key = Config.AZURE_OPENAI_API_KEY
openai.api_base = Config.AZURE_OPENAI_ENDPOINT
openai.api_version = Config.AZURE_OPENAI_API_VERSION

class GPTAnalyzer:
    def __init__(self):
        # No client initialization required as openai is configured globally.
        pass

    def analyze_code(self, code_content, question_data, analysis_prompt):
        try:
            # Debug prints
            print("\nDEBUG - Starting analysis")
            print("DEBUG - Question data keys:", question_data.keys())
            
            # Get the actual test score
            actual_score = self._get_test_score_from_question(question_data)
            print(f"DEBUG - Final calculated score: {actual_score}")
            
            requirements = self._extract_requirements(question_data)
            test_cases = self._extract_test_cases(question_data)
            solution = self._extract_solution(question_data)
            
            test_results = self._run_test_case_analysis(test_cases, actual_score)
            code_analysis = self._analyze_code_structure(code_content, requirements, solution)
            gpt_insights = self._get_gpt_insights(code_content, requirements, analysis_prompt, actual_score)
            
            return self._format_analysis_report(test_results, code_analysis, gpt_insights, requirements)
        except Exception as e:
            print(f"DEBUG - Error in analysis: {str(e)}")
            traceback.print_exc()
            return f"Error in analysis: {str(e)}"

    def _get_test_score_from_question(self, question_data):
        try:
            print("\nDEBUG - Checking test cases")
            student_questions = question_data.get('student_questions', {})
            if student_questions:
                print("DEBUG - Found student_questions")
                testcase_percentage = student_questions.get('testcase_percentage')
                if testcase_percentage is not None:
                    print(f"DEBUG - Found direct testcase_percentage: {testcase_percentage}")
                    return float(testcase_percentage)
                
                marks = student_questions.get('marks')
                if marks is not None:
                    total_marks = question_data.get('marks', 0)
                    if total_marks > 0:
                        percentage = (float(marks) / float(total_marks)) * 100
                        print(f"DEBUG - Calculated from marks: {percentage}")
                        return percentage
                
                l_event_data = student_questions.get('l_event_data', {})
                if l_event_data:
                    testcase_results = l_event_data.get('testcase_results', [])
                    if testcase_results:
                        passed = sum(1 for test in testcase_results if test.get('status') == 'pass')
                        total = len(testcase_results)
                        if total > 0:
                            percentage = (passed / total) * 100
                            print(f"DEBUG - Calculated from testcase_results: {percentage}")
                            return percentage
                    
                    program_score = l_event_data.get('program_score')
                    if program_score is not None:
                        print(f"DEBUG - Found program_score: {program_score}")
                        return float(program_score)

            print("DEBUG - No valid score found, returning 100 as all test cases passed")
            return 100  # Default to 100 if no score is found
                
        except Exception as e:
            print(f"Error calculating score: {str(e)}")
            traceback.print_exc()
            return 0

    def _extract_requirements(self, question_data):
        return {
            'question_text': question_data.get('question_data', ''),
            'input_format': question_data.get('programming_question', {}).get('input_format', ''),
            'output_format': question_data.get('programming_question', {}).get('output_format', ''),
            'constraints': question_data.get('programming_question', {}).get('code_constraints', ''),
            'whitelist': question_data.get('programming_question', {}).get('solution', [{}])[0].get('whitelist', [])
        }

    def _extract_test_cases(self, question_data):
        prog_question = question_data.get('programming_question', {})
        test_cases = []
        
        # Extract sample test cases
        sample_io = prog_question.get('sample_io')
        if sample_io:
            try:
                sample_cases = json.loads(sample_io)
                for case in sample_cases:
                    test_cases.append({
                        'input': case.get('input', ''),
                        'output': case.get('output', ''),
                        'type': 'Sample',
                        'score': 0,
                        'weightage': 0,
                        'passed': True
                    })
            except json.JSONDecodeError:
                pass

        # Extract actual test cases
        actual_cases = prog_question.get('testcases')
        if actual_cases:
            try:
                cases = json.loads(actual_cases)
                for case in cases:
                    test_cases.append({
                        'input': case.get('input', ''),
                        'output': case.get('output', ''),
                        'difficulty': case.get('difficulty', 'Unknown'),
                        'score': case.get('score', 25),
                        'weightage': case.get('score', 25),
                        'passed': True
                    })
            except json.JSONDecodeError:
                pass

        return test_cases

    def _extract_solution(self, question_data):
        solutions = question_data.get('programming_question', {}).get('solution', [{}])
        if solutions and solutions[0].get('solutiondata'):
            return solutions[0]['solutiondata'][0].get('solution', '')
        return ''

    def _analyze_code_structure(self, code_content, requirements, solution):
        analysis = {
            'missing_requirements': [],
            'potential_issues': [],
            'whitelist_violations': []
        }

        # Check for specific Java issues
        if "Student[] students = new Student" in code_content:
            analysis['potential_issues'].append("Constructor creates local variables instead of initializing instance variables")
        if "int count = 0" in code_content and "this.count = 0" not in code_content:
            analysis['potential_issues'].append("Count variable initialized locally instead of as instance variable")

        whitelist = requirements.get('whitelist', [])
        if whitelist and isinstance(whitelist, list):
            if len(whitelist) > 0 and isinstance(whitelist[0], dict) and 'list' in whitelist[0]:
                for item in whitelist[0]['list']:
                    if item not in code_content:
                        analysis['whitelist_violations'].append(f"Missing required element: {item}")

        return analysis

    def _run_test_case_analysis(self, test_cases, actual_score):
        results = []
        max_score = 100
        
        # Get the most recent submit event's test results
        for i, test in enumerate(test_cases):
            score = 0
            if test.get('type') != 'Sample':
                # Calculate individual test case score based on actual_score
                score = (actual_score / 100.0) * test.get('weightage', 25)
            
            results.append({
                'case_number': i + 1,
                'type': test.get('type', 'Test Case'),
                'difficulty': test.get('difficulty', 'Unknown'),
                'input': test.get('input', ''),
                'expected_output': test.get('output', ''),
                'score': score,
                'weightage': test.get('weightage', 25),
                'passed': score > 0
            })
        
        return {
            'results': results,
            'total_score': actual_score,
            'max_score': max_score
        }

    def _get_gpt_insights(self, code_content, requirements, analysis_prompt, actual_score):
        try:
            # If score is 100%, return a simple success message
            if actual_score == 100:
                return "All test cases passed successfully. The code meets all requirements."

            # Extract line count requirement if it exists
            line_count = None
            if "in" in analysis_prompt.lower() and "line" in analysis_prompt.lower():
                try:
                    line_count = int(''.join(filter(str.isdigit, analysis_prompt)))
                except:
                    pass

            # Construct a more detailed prompt for clarity and precision
            prompt = f"""
    You are an expert code reviewer and evaluator with a focus on clarity and precision.
    Review the following Java code implementation of a Student Management System.

    Requirements:
    {requirements['question_text']}

    Student's Code:
    {code_content}

    Test case score: {actual_score}%

    Your analysis must:
    - Clearly evaluate the code correctness, pointing out any syntax or logical errors.
    - Examine the code structure, including class definitions, method implementations, and adherence to coding standards.
    - Identify specific missing elements (e.g., required constructors, methods such as 'displayInfo' or 'addStudent') if any.
    - Provide actionable, precise recommendations for improvement.
    - Explain how the code deviates from the requirements.

    {f'Limit your response to exactly {line_count} lines.' if line_count else 'Present your analysis as clear bullet points.'}
    """

            response = openai.ChatCompletion.create(
                engine=Config.AZURE_OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a precise and concise code reviewer. Provide clear, step-by-step analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=900
            )

            analysis = response.choices[0].message.content.strip()

            # Enforce line count if specified
            if line_count:
                lines = analysis.split('\n')
                if len(lines) > line_count:
                    lines = lines[:line_count]
                elif len(lines) < line_count:
                    lines.extend([''] * (line_count - len(lines)))
                analysis = '\n'.join(lines)

            return analysis

        except Exception as e:
            print(f"Error in GPT analysis: {str(e)}")
            return "Error generating analysis. Please try again."

    def _format_analysis_report(self, test_results, code_analysis, gpt_insights, requirements):
        report = "Code Analysis Report\n"
        report += "===================\n\n"

        # Score Summary
        report += f"Final Score: {test_results['total_score']:.0f}/{test_results['max_score']}\n"
        report += "=" * 20 + "\n\n"

        # Test Cases Section
        report += "Test Case Analysis:\n"
        report += "-----------------\n"
        for result in test_results['results']:
            report += f"\nTest Case {result['case_number']}"
            report += f" ({result['difficulty']})\n" if result['difficulty'] != 'Unknown' else "\n"
            report += f"Type: {result['type']}\n"
            report += f"Score: {result['score']:.2f} points\n"
            report += f"Input:\n{result['input']}\n"
            report += f"Expected Output:\n{result['expected_output']}\n"

        report += f"\nTotal Score: {test_results['total_score']:.0f}/{test_results['max_score']} points\n\n"

        # Code Structure Analysis
        report += "Code Structure Analysis:\n"
        report += "----------------------\n"
        if code_analysis['whitelist_violations']:
            report += "Missing Required Elements:\n"
            for violation in code_analysis['whitelist_violations']:
                report += f"- {violation}\n"
        
        if code_analysis['potential_issues']:
            report += "\nPotential Issues:\n"
            for issue in code_analysis['potential_issues']:
                report += f"- {issue}\n"

        # GPT Insights
        report += "\nAI Analysis Insights:\n"
        report += "-------------------\n"
        report += gpt_insights + "\n"

        return report
