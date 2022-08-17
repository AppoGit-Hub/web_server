from datetime import timedelta

JSON_FILE_LOAD_SUCCES = 0
JSON_FILE_LOAD_FAIL = 1
JSON_FILE_DOESNT_EXISTS = 2
JSON_FILE_DUMPS_SUCCES = 3
JSON_FILE_DUMPS_FAIL = 4

FOLLOW_PATH_SUCCES = 0
FOLLOW_PATH_CANT_FIND_KEY = 1
FOLLOW_PATH_VALUE_ISNT_DICT = 2
FOLLOW_PATH_PATH_MUST_HAVE_AT_LEAST_ONE_KEY = 3
FOLLOW_PATH_NO_ERROR = 4

FILE_TYPE_IMAGE = 0
FILE_TYPE_TEXT = 1

ERROR_TYPE_COULDNT_FIND_STAT_TYPE = 1
ERROR_TYPE_COULDNT_FIND_STAT_NAME = 2

DATA_FOLDER = "../data"

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
FILE_STAT_TEMPLATE = "followers_%s_%s.json"

ERROR_TYPE_DESCRIPTION = {
    ERROR_TYPE_COULDNT_FIND_STAT_TYPE : "Couldnt find this type of stats",
    ERROR_TYPE_COULDNT_FIND_STAT_NAME : "Couldnt find this name of stat"
}

GRAPH_REFRESH_DELAY = 7 #in days
DATA_SAVE_FILENAME = "router_refresh_data.json"
API_PERMANENT_DATA_FILENAME = "follower_refresh_data.json"
TIME_DELTA_REFRESH = timedelta(days=GRAPH_REFRESH_DELAY)

AVERAGES_NAME_TO_FILENAME = {
    "like" : "followers_average_like.json",
    "quote" : "followers_average_quote.json",
    "reply" : "followers_average_reply.json",
    "retweet" : "followers_average_retweet.json",
}

TOTALS_NAME_TO_FILENAME = {
    "like" : "followers_total_like.json",
    "quote" : "followers_total_quote.json",
    "reply" : "followers_total_reply.json",
    "retweet" : "followers_total_retweet.json",
    "tweet" : "followers_total_tweet.json"
}

TIMES_NAME_TO_FILENAME = {
    "hour" : "followers_hour_create_at.json",
    "day" : "followers_day_create_at.json",
}

STATS_TYPES_WITH_NAMES = {
    "average" : AVERAGES_NAME_TO_FILENAME,
    "total" : TOTALS_NAME_TO_FILENAME,
    "time" : TIMES_NAME_TO_FILENAME
}

"""
STATS_TYPES_WITH_NAMES = {
    "average" : [
        "like",
        "quote",
        "reply",
        "retweet"
    ],
    "total" : [
        "like",
        "quote",
        "reply",
        "retweet",
        "tweet"
    ],
    "time" : [
        "hour",
        "day"
    ]
}
"""

API_IP = "192.168.1.7"
API_PORT = 8000
API_ADDRESS = f"{API_IP}:{API_PORT}"

HOST_IP = "192.168.1.7"
HOST_PORT = 80
HOST_ADDRESS = f"{HOST_IP}:{HOST_PORT}"