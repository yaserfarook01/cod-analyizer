class FileHandler:
    def save_analysis(self, coding_answers, analysis_prompt, analyzer):
        with open('analysis_report.txt', 'w', encoding='utf-8') as f:
            for i, answer in enumerate(coding_answers, 1):
                f.write(f"\nQuestion {i}:\n")
                f.write(f"Language: {answer['language']}\n")
                f.write(f"File: {answer['filename']}\n")
                f.write("\nStudent's Code:\n")
                f.write("-------------\n")
                f.write(answer['content'])
                f.write("\n\nAnalysis Report:\n")
                f.write("---------------\n")
                
                analysis = analyzer.analyze_code(
                    answer['content'],
                    answer['question_data'],
                    analysis_prompt
                )
                f.write(analysis)
                f.write("\n" + "="*50 + "\n")
