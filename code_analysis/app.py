import streamlit as st
from code_extractor import CodeExtractor

def parse_report(report_text):
    """
    Splits the report into sections based on known headers.
    Assumes the report contains headers such as:
    - "Final Score:"
    - "Test Case Analysis:"
    - "Code Structure Analysis:"
    - "AI Analysis Insights:"
    """
    sections = {
        "Final Score": "",
        "Test Case Analysis": "",
        "Code Structure Analysis": "",
        "AI Analysis Insights": ""
    }
    
    current_header = None
    for line in report_text.splitlines():
        if "Final Score:" in line:
            current_header = "Final Score"
            sections[current_header] += line + "\n"
        elif "Test Case Analysis:" in line:
            current_header = "Test Case Analysis"
            sections[current_header] += line + "\n"
        elif "Code Structure Analysis:" in line:
            current_header = "Code Structure Analysis"
            sections[current_header] += line + "\n"
        elif "AI Analysis Insights:" in line:
            current_header = "AI Analysis Insights"
            sections[current_header] += line + "\n"
        elif current_header:
            sections[current_header] += line + "\n"
    return sections

def main():
    st.title("Code Analyzer")
    
    st.markdown("### Enter Details")
    url = st.text_input("Enter the URL:", placeholder="https://admin.ltimindtree.iamneo.ai/result?testId=...")
    auth_token = st.text_area("Enter the Authorization Token:", placeholder="eyJhbGciOiJIUzI1...")
    analysis_prompt = st.selectbox(
        "Select Analysis Focus:",
        [
            "Check why the testcase failed, give in 3 lines",
            "Check if the code has logical errors and syntax issues only",
            "Verify if the code meets the basic requirements and handles edge cases",
            "Identify any missing critical functionality",
            "Check for proper error handling and validation",
            "Custom Analysis"
        ]
    )
    if analysis_prompt == "Custom Analysis":
        analysis_prompt = st.text_area(
            "Enter your custom analysis criteria:",
            placeholder="Example: Check if the code handles null inputs and implements proper validation"
        )

    if st.button("Analyze Code"):
        if url and auth_token:
            with st.spinner("Processing and analyzing code..."):
                extractor = CodeExtractor()
                result, success = extractor.get_coding_answers(url, auth_token, analysis_prompt)
                if success:
                    st.success("Analysis complete!")
                    
                    # Read the generated analysis report
                    try:
                        with open('analysis_report.txt', 'r', encoding='utf-8') as file:
                            report_text = file.read()
                    except Exception as e:
                        st.error(f"Error reading report file: {str(e)}")
                        return

                    # Optionally, provide a download button
                    st.download_button(
                        label="Download Analysis Report",
                        data=report_text,
                        file_name="analysis_report.txt",
                        mime="text/plain"
                    )
                    
                    st.markdown("## Analysis Preview")
                    
                    # Parse the report into sections
                    sections = parse_report(report_text)
                    
                   # Display each section in an expander for clarity
                    if sections.get("Final Score"):
                        with st.expander("Final Score", expanded=True):
                            st.markdown("```\n" + sections["Final Score"] + "\n```")
                    if sections.get("Test Case Analysis"):
                        with st.expander("Test Case Analysis", expanded=True):
                            st.markdown("```\n" + sections["Test Case Analysis"] + "\n```")
                    if sections.get("Code Structure Analysis"):
                        with st.expander("Code Structure Analysis", expanded=True):
                            st.markdown("```\n" + sections["Code Structure Analysis"] + "\n```")
                    if sections.get("AI Analysis Insights"):
                        with st.expander("AI Analysis Insights", expanded=True):
                            st.markdown("```\n" + sections["AI Analysis Insights"] + "\n```")

                else:
                    st.error(f"Failed to process: {result}")
        else:
            st.warning("Please enter both URL and Authorization Token.")

    with st.expander("How to use"):
        st.markdown("""
        1. Enter the URL from the admin panel.
        2. Enter your Authorization Token.
        3. Select the type of analysis you want.
        4. Click **Analyze Code**.
        5. Download the analysis report and review the detailed sections.
        
        The report will include:
        - The original code.
        - Test case analysis.
        - Code structure analysis.
        - AI analysis insights.
        """)

if __name__ == "__main__":
    main()
