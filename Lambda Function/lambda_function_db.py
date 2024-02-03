import datetime
import boto3
from datetime import date
import calendar


# Dynamo db client
boto_client = boto3.resource("dynamodb", region_name="eu-north-1")
dynamo_db_table = boto_client.Table("electric_data")


def hour_rounder(t):
    return t.replace(
        second=0, microsecond=0, minute=0, hour=t.hour
    ) + datetime.timedelta(hours=t.minute // 30)


def get_date_keys():
    """Gets the date range of data 2 minutes before current"""
    date_keys = []
    end_range = hour_rounder(datetime.datetime.today())
    start_range = end_range - datetime.timedelta(hours=24)
    while start_range <= datetime.datetime.today():
        start_range += datetime.timedelta(minutes=15)
        date_keys.append(int(start_range.strftime("%Y%m%d%H%M%S")))

    return date_keys


def convert_to_epoch(interconnector_data):
    """Converts date string to epoch time as javascript front end needs epoch"""
    for i in range(len(interconnector_data["Responses"]["electric_data"])):
        time_stamp = datetime.datetime.strptime(
            str(interconnector_data["Responses"]["electric_data"][i]["datetime"]),
            "%Y%m%d%H%M%S",
        )
        interconnector_data["Responses"]["electric_data"][i][
            "datetime"
        ] = calendar.timegm(time_stamp.timetuple())
    return interconnector_data


def get_todays_data_from_db():
    """
    Returns the data for today from the database
    """
    data = boto_client.batch_get_item(
        RequestItems={
            "electric_data": {
                "Keys": [
                    {"datetime": dt, "date": int(str(dt)[:8])} for dt in get_date_keys()
                ]
            }
        }
    )
    # Sort the data by datetime
    data["Responses"]["electric_data"] = sorted(
        data["Responses"]["electric_data"], key=lambda x: x["datetime"]
    )
    data = convert_to_epoch(data)
    return data


def lambda_handler(event, context):

    return {"statusCode": 200, "body": get_todays_data_from_db()}


# get_todays_data_from_db()
