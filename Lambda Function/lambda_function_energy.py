import pandas as pd
from entsoe import EntsoePandasClient
import datetime
import boto3
import json

uk_country_code = "UK"  #
country_code_non_uk_dict = {
    "France": "FR",
    "Netherlands": "NL",
    "Belgium": "BE",
    "Norway": "NO",
}

ssm_client = boto3.client("ssm")
api_key = ssm_client.get_parameter(Name="entsoe-api-token", WithDecryption=False)

# Defining client
client = EntsoePandasClient(api_key=api_key["Parameter"]["Value"])

# Dynamo db client
boto_client = boto3.resource("dynamodb")
dynamo_db_table = boto_client.Table("interconnector-data")


def get_date_range():
    """Gets the date range of data 2 minutes before current"""
    twenty_four_hours = datetime.datetime.today() - datetime.timedelta(days=1)
    tomorrow = datetime.datetime.today() + datetime.timedelta(hours=2)
    return {
        "start": pd.Timestamp(
            twenty_four_hours.strftime("%Y-%m-%d %H:%M:%S"), tz="UTC"
        ),
        "end": pd.Timestamp(tomorrow.strftime("%Y-%m-%d %H:%M:%S"), tz="UTC"),
    }


def get_net_flow(start_end_range, country_code):
    """Get each net flow between UK and specified country code and returns a series
    Args:
        start_end_range (dict): dictionary of 2 timestamps for start and end
        country_code (string): country code to query
    """
    flows_outward_from_uk = client.query_crossborder_flows(
        uk_country_code,
        country_code,
        start=start_end_range["start"],
        end=start_end_range["end"],
    )
    flows_inward_to_uk = client.query_crossborder_flows(
        country_code,
        uk_country_code,
        start=start_end_range["start"],
        end=start_end_range["end"],
    )
    return flows_outward_from_uk - flows_inward_to_uk


def get_all_interconnector_flows(country_code_non_uk_dict):
    """Function to get all interconnector flows and returns

    Args:
        start_end_range (dict): dictionary of 2 timestamps for start and end
        country_code_non_uk_dict (dict): dictionary of non uk country codes
    """
    all_interconnector_dict = {}
    for country in list(country_code_non_uk_dict.keys()):
        all_interconnector_dict[country] = get_net_flow(
            get_date_range(), country_code_non_uk_dict[country]
        )
    return pd.concat(all_interconnector_dict, axis=1).ffill()


def convert_df_datetime_to_strftime(interconnector_flow_df):
    """Converts the datetime to string

    Args:
        interconnector_flow_df (pd.dataframe): dataframe with interconnector flow
    """
    new_df = interconnector_flow_df.reset_index().rename(columns={"index": "datetime"})
    new_df["date"] = new_df["datetime"].apply(lambda x: int(x.strftime("%Y%m%d")))
    new_df["datetime"] = new_df["datetime"].apply(
        lambda x: int(x.strftime("%Y%m%d%H%M%S"))
    )
    return new_df


def convert_float_to_int(interconnector_flow_df):
    """Converts all floats to int

    Args:
        interconnector_flow_df (pd.dataframe): _description_
    """
    return interconnector_flow_df.apply(lambda x: x.astype(int))


def convert_df_to_json(interconnector_flow_df):
    """Converts the df to json ready for input to dynamodb

    Args:
        interconnector_flow (pd.Dataframe): dataframe with json ready for input to dynamodb
    """
    return json.loads(interconnector_flow_df.reset_index().to_json(orient="records"))


def check_if_exists(input):
    """Checks to see if the item exists in the dynamodb table already

    Args:
        input (dict): Dictionary of interconnectorflow_df
    """
    response = dynamo_db_table.get_item(
        Key={"datetime": input["datetime"], "date": input["date"]}
    )
    if "Item" in response:
        return True
    return False


def put_into_dynamo_db(input):
    """Puts the input into dynamodb table

    Args:
        input (dict): entry for db table
    """
    if check_if_exists(input) == False:
        dynamo_db_table.put_item(Item=input)


def update_dynamo_db(interconnector_dict):
    """Function to update dynamo db

    Args:
        interconnector_dict (dict): full interconnector dictionary
    """
    # Efficiency can be improved here by using get batch item so doesn't check for each item
    for entry in interconnector_dict:
        put_into_dynamo_db(entry)


def lambda_handler(event, context):
    try:
        interconnector_df = get_all_interconnector_flows(country_code_non_uk_dict)
        interconnector_df = convert_float_to_int(interconnector_df)
        interconnector_df = convert_df_datetime_to_strftime(interconnector_df)
        interconnector_df.set_index("datetime", inplace=True)
        interconnector_dict = convert_df_to_json(interconnector_df)
        update_dynamo_db(interconnector_dict)
        return {"statusCode": 200, "body": json.dumps("Everything works!")}
    except:
        raise Exception
