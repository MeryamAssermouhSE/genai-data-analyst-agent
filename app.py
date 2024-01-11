import streamlit as st
from src.llm import question_to_query, result_to_answer
from src.bigquery import get_bq_result
from tables_info import get_table_info_and_write_to_file
from google.cloud import bigquery
from google.auth import exceptions as auth_exceptions
import json
from src.correct_query import correct_query

def dry_run_query(client, sql_query):
    query_job_config = bigquery.QueryJobConfig(dry_run=True)
    query_job = client.query(sql_query, job_config=query_job_config)
    return query_job.total_bytes_processed

def main():
    st.title("Data Analyst Agent")
    client = bigquery.Client()
    if client:

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
            if st.button("Dry Run"):
                query = question_to_query(input_question=input_question, database_info=database_info, prompt_format=engineered_prompt)
                sql_query = query.candidates[0].text
                
                sql_query = correct_query(sql_query)
                
                # Perform a dry run to estimate bytes processed
                bytes_processed = dry_run_query(client, sql_query)

                st.write(f"This query will process {bytes_processed/1024:.2f} KB when run")
            if st.button("Run Analysis"):

                query = question_to_query(input_question=input_question, database_info=database_info, prompt_format=engineered_prompt)
                sql_query = query.candidates[0].text
                
                sql_query = correct_query(sql_query)
                
                #print('quey type: ',type(sql_query))
                # Execute the query
                query_result = get_bq_result(sql_query)
                query_result = json.loads(query_result)

                n = len(query_result)

                if n<=10:
                    # the prompt to geenrate the answer
                    engineered_prompt_1 = "I ran this sql query : {query_script}, and I got this result : {query_result}. Use the query result to formulate a clear and straightforward user friendly answer to this question : {question}. Give me the answer in natural language ready to be read by the end user, without quotation marks or anything"

                    # Create an answer
                    answer = result_to_answer(input_question=input_question, query_script=sql_query, query_result=query_result,
                                            prompt_format=engineered_prompt_1)

                    # Display the final answer
                    st.write("Final Answer:")
                    st.write(answer.candidates[0].text)

                    # Display the SQL query
                    with st.expander("View SQL Query", expanded=False):
                        st.write(sql_query)
                    # Display the query result
                    with st.expander("View Query Result", expanded=False):
                        st.table(query_result)
                
                else : 
                    
                    #take only 10 first rows bc result is too long
                    query_result = query_result[:10]
                    # the prompt to geenrate the answer
                    engineered_prompt_1 = "I ran this sql query : {query_script}, and from the result I selected the first 10 rows : {query_result}. Use this information to formulate a clear and straightforward user friendly answer to this question : {question}. Keep in mind that the complete result contains "+str(n)+" rows, and this is just a sample for reference. Give me the answer in natural language ready to be read by the end user, without quotation marks or anything"

                    # Create an answer
                    answer = result_to_answer(input_question=input_question, query_script=sql_query, query_result=query_result,
                                            prompt_format=engineered_prompt_1)

                    # Display the final answer
                    st.write("Summary Answer:")
                    st.write(answer.candidates[0].text)

                    # Display the SQL query
                    with st.expander("View SQL Query", expanded=False):
                        st.write(sql_query)
                    # Display the query result
                    with st.expander("View Query Result", expanded=False):
                        st.write("The result contains " +str(n)+" rows. This is just a sample : ")
                        st.table(query_result)



        else:
            st.warning("No datasets available. Make sure the authenticated user has the necessary permissions.")


if __name__ == "__main__":
    main()
