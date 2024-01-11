from src.llm import load_llm_model
from vertexai.preview.language_models import TextGenerationModel
from src.bigquery import get_bq_result
import json
import ast
from src.embedding import get_text_embeddings, find_most_similar_vector


def predict(
    prompt: str,
    llm_model: TextGenerationModel = load_llm_model(),
    max_output_tokens: int = 1024,
    temperature: float = 0.1,
    top_p: float = 0.8,
    top_k: int = 40,
):
    
    answer = llm_model.predict(
        prompt,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
    )

    return answer

def replace_words_in_string(input_string, list1, list2):
    result = []
    i = 0
    while i < len(input_string):
        if input_string[i] == "'":
            # Find the end of the quoted substring
            end_quote_index = input_string.find("'", i + 1)
            if end_quote_index != -1:
                quoted_substring = input_string[i + 1 : end_quote_index]
                if quoted_substring in list1:
                    index = list1.index(quoted_substring)
                    result.append("'" + list2[index] + "'")
                else:
                    result.append("'" + quoted_substring + "'")
                i = end_quote_index + 1
                continue
        result.append(input_string[i])
        i += 1

    output_string = ''.join(result)
    return output_string

def correct_query(query):

    #check if query contains filters with string values
    if "where" not in query:
        return query
    else :
        #initial check
        print('initial query : ',query)
        with open('data/table_info.txt') as file:
                database_info = file.read()
        ppt = "use this information about the database and column types : '{info}', and see if this query : '{query}' has any formatting mistakes such as string values used without quotation marks like'..'. If you find any mistakes correct them. Give me back only the sql query without any additional text or quotation marks, just the sql ready to copy and paste and run."
        ppt = ppt.format(info=database_info,query=query)
        query = predict(ppt)
        query = query.candidates[0].text
        print('query after first check : ',query)
    #if yes get names of filter columns
        prompt_template = "take this sql query : '{query}', and extract the names of the columns used in the where clause and that have string values as filter. give me the result as a python list of strings, where the strings are the names of the columns. Don't add any additional text just the list."
        prompt = prompt_template.format(query=query)
        column_list = predict(prompt)
        column_list=column_list.candidates[0].text
        column_list = ast.literal_eval(column_list)
        prompt_template1 = "take this sql query : '{query}', and extract the string filter values used with these columns : {list} in the where clause. give me the result as a python list of strings, where the strings are the names of the filter values. Don't add any additional text just the list. for example if there is where col = 'val', then 'val' is a filter values. Make sure to put the filter values in the same order as the provided list of columns."
        prompt1 = prompt_template1.format(query=query, list=column_list)
        values_list = predict(prompt1)
        values_list=values_list.candidates[0].text
        values_list = ast.literal_eval(values_list)
        print(values_list)

    # for each column in the list select all values and vectorize them
        corrected_values = []
        for i, col in enumerate(column_list):
            value = values_list[i]
            pmpt_tmpl="get the table name and database used in this sql query : '{query}'"
            pmpt = pmpt_tmpl.format(query=query,col=col)
            data = predict(pmpt)
            data = data.candidates[0].text
            pmpt_tmpl1 = "use the database and table name specified in this statement : '{data}', and replace them in the sql query 'select {col} from database.table;'. give me the final sql query ready to copy and pase without quetation marks or any additional text. Make sure it's lowercase."
            pmpt1 = pmpt_tmpl1.format(data= data,col = col)
            sql = predict(pmpt1)
            sql = sql.candidates[0].text
            col_values = get_bq_result(sql)
            col_values = json.loads(col_values)
            col_values = [element[col] for element in col_values]
            #get list of embeddings
            embeddings = get_text_embeddings(col_values)
            value_embedding = get_text_embeddings([value])[0]

            #compute similarity and get index of closest actual value
            i = find_most_similar_vector(embeddings,value_embedding)
            corrected_values.append(col_values[i])

        print('corrected values : ',corrected_values)
    # replace filter value with most similar existing value
        #prompt_template2 = "take this sql query : '{query}'. It contains the following values as filter values in the where clause : '{values}'. Make sure to use quotation marks with the filter values if they are of type string. Give me back the new sql query without quotation marks or any additional text, I want to be able to copy and paste it and run it directly."
        #prompt2 = prompt_template2.format(query=query, values = values_list, correct_values=corrected_values)
        #valid_query = predict(prompt2)
        #valid_query=valid_query.candidates[0].text
        valid_query = replace_words_in_string(query,values_list,corrected_values)
        print('valid query : ',valid_query)

    return valid_query

if __name__=="__main__":
    valid_query = correct_query("select year from movie_insights.movie_score where name = 'the robinson'")
    print(valid_query)
    print(type(valid_query))