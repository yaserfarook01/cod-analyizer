import streamlit as st
from code_extractor import CodeExtractor

def main():
    st.title("Code Analyzer")

    # Input fields
    url = st.text_input("Enter the URL:", placeholder="https://admin.ltimindtree.iamneo.ai/result?testId=...")
    auth_token = st.text_area("Enter the Authorization Token:", placeholder="eyJhbGciOiJIUzI1...")

    # Analysis prompt selection
    analysis_prompt = st.selectbox(
        "Select Analysis Focus:",
        [
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

    # Process button
    if st.button("Analyze Code"):
        if url and auth_token:
            with st.spinner("Processing and analyzing code..."):
                extractor = CodeExtractor()
                result, success = extractor.get_coding_answers(url, auth_token, analysis_prompt)
                
                if success:
                    st.success("Analysis complete!")
                    
                    with open('cod.txt', 'r', encoding='utf-8') as file:
                        content = file.read()
                        st.download_button(
                            label="Download Analysis Report",
                            data=content,
                            file_name="cod.txt",
                            mime="text/plain"
                        )
                    
                    st.subheader("Analysis Preview:")
                    st.text(content)
                else:
                    st.error(f"Failed to process: {result}")
        else:
            st.warning("Please enter both URL and Authorization Token.")

    with st.expander("How to use"):
        st.markdown("""
        1. Enter the URL from the admin panel
        2. Enter your Authorization Token
        3. Select the type of analysis you want
        4. Click "Analyze Code"
        5. Download the analysis report
        
        The report will include:
        - Original code
        - Focused 3-line analysis based on selected criteria
        """)

if __name__ == "__main__":
    main()