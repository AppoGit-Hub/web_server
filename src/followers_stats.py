from datetime import datetime, timedelta
import time
import tweepy
import json
import rfc3339
import constant
import utils

GET_FOLLOWER_STATS = 1
CREATE_GRAPH = 2

DO = CREATE_GRAPH

DAY_RANGE = 7

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

FOLLOWERS_STATS_FILENAME = "followers_stats.json"
GLOBAL_FOLLOWERS_STATS_FILENAME = "global_followers_stats.json"

FILE_TOTAL_TEMPLATE = "followers_total_%s.json"
FILE_AVERAGE_TEMPLATE = "followers_average_%s.json"
TITLE_TOTAL_TEMPLATE = "Total %s on the last 7 days"
TITAL_AVERAGE_TEMPLATE = "Average %s on the last 7 days"

keys, error = utils.read_json_from_file(utils.get_path_for_resource("keys.json"))
if error != constant.JSON_FILE_LOAD_SUCCES:
    print(f"Couldnt load keys. Got {error}")

client = tweepy.Client(
    bearer_token = keys["BEARER_TOKEN"],
    access_token = keys["ACCES_TOKEN"],
    consumer_key = keys["CONSUMER_API_KEY"],
    consumer_secret= keys["CONSUMER_KEY_SECRET"],
    access_token_secret = keys["ACCES_TOKEN_SECRET"],
    wait_on_rate_limit = True)

def read_json_from_file(filepath):
    with open(filepath, "r") as file:
        json_data = json.load(file)
    return json_data

def write_json_from_file(filepath, dict_to_write):
    with open(filepath, "w") as file:
        file.write(json.dumps(dict_to_write, indent=4))

def display_narrow(dict, stat):
    for index, (username, metric) in enumerate(dict.items()):
        print(f"{index+1} : {username} - {metric[stat]}")

def create_average(filename, global_followers_stats, metric):
    average_sorted = {}        
    with open(filename, "w") as global_followers_stats_narrow:
        global_sorted_narrow = {}
        for sorted_key, sorted_value in global_followers_stats.items():
            global_sorted_narrow.update({sorted_key : sorted_value[metric] / sorted_value["tweet_count"]})

        average_sorted = dict(sorted(global_sorted_narrow.items(), key=lambda item: item[1], reverse=True))
        global_followers_stats_narrow.write(json.dumps(average_sorted, indent=4))
    return average_sorted

def create_follower_stats():
    api_permanent_file = read_json_from_file(utils.get_path_for_resource(constant.API_PERMANENT_DATA_FILENAME))

    last_time_got_followers_stats = datetime.strptime(api_permanent_file["last_time_got_followers_stats"], DATE_TIME_FORMAT)
    today = datetime.utcnow()
    timedelta_refresh_deltay = constant.TIME_DELTA_REFRESH
    delta_time_refresh = today -  last_time_got_followers_stats
    follower_stats_need_a_refresh : bool = delta_time_refresh > timedelta_refresh_deltay

    followers_stats = {}
    global_followers_stats = {}

    if follower_stats_need_a_refresh:
        print(f"Refreshing followers stats. Asking Twitter's API. Delta time: {delta_time_refresh}")
        one_week_ago = today - timedelta_refresh_deltay
        one_week_ago = rfc3339.rfc3339(one_week_ago)

        me = client.get_me()

        total_tweets_count = 0
        total_request_count = 0
        start_time = time.perf_counter()

        me_user_following = client.get_users_following(me.data.id)
        for following_user in me_user_following.data:
            #sleep(3)
            following_user_name = following_user.username
            following_user_id = following_user.id
            
            following_user_data = {
                following_user_name : []
            }
            
            following_user_tweets = client.get_users_tweets(id=following_user_id, start_time=one_week_ago, tweet_fields=['public_metrics', 'created_at'], max_results=100, exclude="retweets")
            tweets_count = following_user_tweets.meta['result_count']
            total_request_count += 1

            if tweets_count > 0:
                print(f"{following_user_name} has {tweets_count} tweets")
                for following_user_tweet in following_user_tweets.data:
                    tweet = {}
                    tweet.update(following_user_tweet.public_metrics)
                    tweet.update({ "created_at" : str(following_user_tweet.created_at) })

                    following_user_data[following_user_name].append(tweet)
                followers_stats.update(following_user_data)
                total_tweets_count += tweets_count
            else:
                print(f"{following_user_name} has no tweet")

        finish_time = time.perf_counter()
        delta_time = finish_time - start_time
        print(f"{total_tweets_count} tweets polled in {delta_time} secs in {total_request_count} request")
        request_per_sec = total_request_count / delta_time
        print(f"{request_per_sec} requests/sec. {request_per_sec * 900} requests/15min")

        api_permanent_file["last_time_got_followers_stats"] = str(today)
        write_json_from_file(utils.get_path_for_resource(constant.API_PERMANENT_DATA_FILENAME), api_permanent_file)

        write_json_from_file(utils.get_path_for_resource(FOLLOWERS_STATS_FILENAME), followers_stats)

        #global_stats are made:

        for username, stats in followers_stats.items():
            global_metric = {
                "retweet_count" : 0,
                "reply_count" : 0, 
                "like_count" : 0, 
                "quote_count" : 0,
                "tweet_count" : 0,
            }
            tweet_count = 0
            for metric in stats:
                global_metric["retweet_count"] += metric["retweet_count"]
                global_metric["reply_count"] += metric["reply_count"]
                global_metric["like_count"] += metric["like_count"]
                global_metric["quote_count"] += metric["quote_count"]
                tweet_count += 1

            global_metric["tweet_count"] = tweet_count

            global_followers_stats.update({username : global_metric})

        write_json_from_file(utils.get_path_for_resource(GLOBAL_FOLLOWERS_STATS_FILENAME), global_followers_stats)
    else:
        print(f"No refresh of followers stats. Pulling from files. Delta time: {delta_time_refresh}")
        followers_stats = read_json_from_file(utils.get_path_for_resource(FOLLOWERS_STATS_FILENAME))
        global_followers_stats = read_json_from_file(utils.get_path_for_resource(GLOBAL_FOLLOWERS_STATS_FILENAME))

    #sub_followers_stats are made:

    def make_narow(filename, metric, value = lambda sorted_value, metric : sorted_value[metric]):
        with open(filename, "w") as global_followers_stats_narrow:
            global_sorted_narrow = {}
            key_function = lambda item: item[1][metric]
            for sorted_key, sorted_value in sorted(global_followers_stats.items(), key=key_function, reverse=True):
                global_sorted_narrow.update({sorted_key : value(sorted_value, metric)})

            global_followers_stats_narrow.write(json.dumps(global_sorted_narrow, indent=4))
        return global_sorted_narrow

    #total_followers
    
    make_narow(utils.get_path_for_resource(FILE_TOTAL_TEMPLATE % 'retweet'), "retweet_count")
    make_narow(utils.get_path_for_resource(FILE_TOTAL_TEMPLATE % 'reply'), "reply_count")
    make_narow(utils.get_path_for_resource(FILE_TOTAL_TEMPLATE % 'like'), "like_count")
    make_narow(utils.get_path_for_resource(FILE_TOTAL_TEMPLATE % 'quote'), "quote_count")
    make_narow(utils.get_path_for_resource(FILE_TOTAL_TEMPLATE % 'tweet'), "tweet_count")

    #hours and days are made...

    def for_each_created_at(follower_dict):
        for username, tweets in follower_dict.items():
            for tweet in tweets:
                create_at = tweet["created_at"]
                created = datetime.strptime(create_at[:len(create_at) - 6], "%Y-%m-%d %H:%M:%S")

                yield created.year, created.month, created.day, created.hour, created.minute, created.second


    hours = [0] * (24)
    num_till_hour = range(24)

    days = [0] * DAY_RANGE
    num_till_day = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    today = datetime.utcnow()

    min_day = 31
    for year, month, day, hour, minute, second in for_each_created_at(followers_stats):
        if day < min_day:
            min_day = day

    for year, month, day, hour, minute, second in for_each_created_at(followers_stats):
        hours[hour] += 1
        days[min_day - day] += 1

    hours_dict = {}
    for hour_index in range(len(hours)):
        hours_dict.update({hour_index : hours[hour_index]})

    write_json_from_file(utils.get_path_for_resource("followers_hour_create_at.json"), hours_dict)

    day_dict = {}
    for day_index in range(len(days)):
        day_dict.update({num_till_day[day_index] : days[day_index]})

    write_json_from_file(utils.get_path_for_resource("followers_day_create_at.json"), day_dict)

    #average_followers_stats are made...

    create_average(utils.get_path_for_resource(FILE_AVERAGE_TEMPLATE % 'like'), global_followers_stats, "like_count")
    create_average(utils.get_path_for_resource(FILE_AVERAGE_TEMPLATE % 'reply'), global_followers_stats, "reply_count")
    create_average(utils.get_path_for_resource(FILE_AVERAGE_TEMPLATE % 'retweet'), global_followers_stats, "retweet_count")
    create_average(utils.get_path_for_resource(FILE_AVERAGE_TEMPLATE % 'quote'), global_followers_stats, "quote_count")

if __name__ == "__main__":
    create_follower_stats()