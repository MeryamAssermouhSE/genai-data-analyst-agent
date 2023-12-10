from google.cloud import bigquery
import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)

def convert_row_iterator_to_json(row_iterator):
    # Extract rows as dictionaries
    rows_as_dicts = [dict(row.items()) for row in row_iterator]

    # Convert to JSON using the custom DecimalEncoder
    json_result = json.dumps(rows_as_dicts, indent=2, cls=DecimalEncoder)

    return json_result

def get_bq_result(sql_query):

    # Set up the BigQuery client
    client = bigquery.Client()

    # Run the query
    job_config = bigquery.QueryJobConfig()
    query_job = client.query(sql_query, job_config=job_config)

    # Get the results
    results = query_job.result()

    results = convert_row_iterator_to_json(results)

    # Return the results
    return results