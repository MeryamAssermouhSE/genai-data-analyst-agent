from google.cloud import bigquery

def get_table_info_and_write_to_file(database_name, output_file_path):
    # Create a BigQuery client
    client = bigquery.Client()

    # Get the dataset object
    dataset_ref = client.dataset(database_name)
    dataset = client.get_dataset(dataset_ref)

    # Get the list of tables in the dataset
    tables = list(client.list_tables(dataset))

    with open(output_file_path, 'w') as output_file:
        for table in tables:
            # Get the table object
            table_object = client.get_table(table)

            # Write table name to the file
            output_file.write(f"Table name is: {table_object.table_id}\n")

            # Fetch the first row of the table
            query = f"SELECT * FROM `{database_name}.{table_object.table_id}` LIMIT 1"
            query_job = client.query(query)
            results = query_job.result()

            # Get the first row
            first_row = next(results)

            # Write column information to the file
            output_file.write("The table contains the following columns:\n")
            for field in table_object.schema:
                output_file.write(f"{field.name} with type {field.field_type}")
                output_file.write(f" and value example {first_row[field.name]}\n")

            output_file.write("\n")

# Example usage
get_table_info_and_write_to_file('movie_insights', 'table_info.txt')
