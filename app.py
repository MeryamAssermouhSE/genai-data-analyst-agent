import streamlit as st
from src.llm import question_to_query, result_to_answer
from src.bigquery import get_bq_result
from tables_info import get_table_info_and_write_to_file
from google.cloud import bigquery
from google.auth import exceptions as auth_exceptions
import json

def authenticate(service_account_key):
    try:
        service_account_key_dict = json.loads(service_account_key)
        client = bigquery.Client.from_service_account_info(service_account_key_dict)
        return client
    except auth_exceptions.GoogleAuthError:
        st.error("Authentication failed. Please make sure your credentials are valid.")
        return None

def main():

    st.title("Data Analyst Agent")

    uploaded_file = st.file_uploader("Upload your Google Cloud service account key JSON file", type="json")


    if uploaded_file is not None:
            try:
                # Read the content of the uploaded service account key file
                service_account_key_content = uploaded_file.read()

                # Authenticate with Google Cloud
                client = authenticate(service_account_key_content)


                if client:

                    st.success("Authentication successful!")

                # Check if datasets are available
                    datasets = list(client.list_datasets())
                    if datasets:
                        database_names = [dataset.dataset_id for dataset in datasets]
                        database_name = st.selectbox("Select a database:", database_names)


                        get_table_info_and_write_to_file(database_name, 'data/table_info.txt')

                        # Reading generated database info
                        with open('data/table_info.txt') as file:
                            database_info = file.read()

                        # User input: question and service account key file
                        input_question = st.text_input("Type your question:")

                        # the prompt to generate the query
                        engineered_prompt = " I have a database with the following informations : {data}. Using these informations, convert the following question : {question} to the simplest SQL query, destined to run in BigQuery. Give me only the SQL script as output ready to copy and paste without quotation marks and make sure to reference the database name and make sure to give meaningful aliases when needed. make sure the script is in lowercase."

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

                    else:
                        st.warning("No datasets available. Make sure the authenticated user has the necessary permissions.")
            except Exception as e:
                st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
