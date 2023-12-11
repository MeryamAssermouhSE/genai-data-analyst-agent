import streamlit as st
from src.llm import question_to_query, result_to_answer
from src.bigquery import get_bq_result

def main():
    st.title("Data Analyst Agent")

    # User input: question and database name
    input_question = st.text_input("Type your question:")

    # Using a static file for db info for now
    with open('data/table_info.txt') as file:
        database_info = file.read()

    # the prompt to generate the query
    engineered_prompt = " I have a database with the following informations : {data}. Using these informations, convert the following question : {question} to the simplest SQL query, destined to run in BigQuery. Give me only the SQL script as output ready to copy and paste without quotation marks and make sure to reference the database name and make sure to give meaningful aliases when needed. make sure the script is in lowercase."

    # Run the analysis on button click
    if st.button("Run Analysis"):

        query = question_to_query(input_question=input_question, database_info=database_info, prompt_format=engineered_prompt)
        sql_query = query.candidates[0].text

        # Display the SQL query
        st.write("Generated SQL Query:")
        st.write(sql_query)

        # Execute the query
        query_result = get_bq_result(sql_query)

        # Display the query result
        st.write("Query Result:")
        st.write(query_result)

        # the prompt to geenrate the answer
        engineered_prompt_1 = "I run this sql query : {query_script}, and I got this result : {query_result}. Use the query result to formulate a clear and straightforward user friendly answer to this question : {question}. Give me the answer in natural language ready to be read by the end user, without quotation marks or anything"

        # Create an answer
        answer = result_to_answer(input_question=input_question, query_script=sql_query, query_result=query_result,
                                  prompt_format=engineered_prompt_1)

        # Display the final answer
        st.write("Final Answer:")
        st.write(answer.candidates[0].text)


if __name__ == "__main__":
    main()
