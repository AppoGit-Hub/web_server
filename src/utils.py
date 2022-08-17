from datetime import datetime
from typing import Tuple
import json
import os
import requests
import socket
import constant

def get_path_for_resource(file_name):
    return f"{constant.DATA_FOLDER}/{file_name}"

def general_to_json(content, func):
    json_content = {}
    try:
        json_content = func(content)
        return json_content, constant.JSON_FILE_LOAD_SUCCES
    except json.JSONDecodeError:
        return json_content, constant.JSON_FILE_LOAD_FAIL

def file_to_json(file_to_load) -> Tuple[object, int]:
    return general_to_json(file_to_load, json.load)

def str_to_json(str_to_load) -> Tuple[object, int]:
    return general_to_json(str_to_load, json.loads)

def from_json(json_content):
    json_str = "un_json_content"
    try:
        json_str = json.dumps(json_content, indent=4)
        return json_str, constant.JSON_FILE_DUMPS_SUCCES
    except:
        return json_str, constant.JSON_FILE_DUMPS_FAIL 

def read_json_from_file(file_path) -> Tuple[object, int]:
    json_content = {}
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="UTF-8") as file:
            return file_to_json(file)
    return json_content, constant.JSON_FILE_DOESNT_EXISTS

def write_json_to_file(file_path, jsoned_content) -> int:
    with open(file_path, "w") as file:
        json_str, error = from_json(jsoned_content)
        if error == constant.JSON_FILE_DUMPS_SUCCES:
            file.write(json_str)
        return error

def extract_year_month_day_hour_minute_seconde_microseconde_from_datetime(date_as_str : str):
    formated_date = datetime.strptime(date_as_str, constant.DATE_TIME_FORMAT)
    return formated_date.year, formated_date.month, formated_date.day, formated_date.hour, formated_date.minute, formated_date.second, formated_date.microsecond

def str_to_datetime(str_datetime) -> datetime:
    return datetime.strptime(str_datetime, constant.DATE_TIME_FORMAT)

def filter_list(list_to_filter : list, condition_filter):
    filtered_list = []
    for thing_to_filter in list_to_filter:
        if condition_filter(thing_to_filter):
            filtered_list.append(thing_to_filter)
    return filtered_list

def follow_path_in_dict(dict_to_explore : dict, dict_keys_path : str, directory_symbole="/"):
    keys_to_follow = dict_keys_path.split(directory_symbole)
    keys_to_follow = filter_list(keys_to_follow, lambda value : value != "")
    
    keys_to_follow_lenght = len(keys_to_follow)
    
    follow_error = constant.FOLLOW_PATH_SUCCES
    end_key_value = dict_to_explore
    
    if keys_to_follow_lenght > 0:
        key_index = 0
        while key_index < keys_to_follow_lenght and follow_error == constant.FOLLOW_PATH_SUCCES:
            key = keys_to_follow[key_index]
            if isinstance(end_key_value, dict):
                try:
                    end_key_value = end_key_value[key]
                except KeyError:
                    follow_error = constant.FOLLOW_PATH_CANT_FIND_KEY
            else:
                follow_error = constant.FOLLOW_PATH_VALUE_ISNT_DICT
            key_index += 1
    else:
        follow_error = constant.FOLLOW_PATH_PATH_MUST_HAVE_AT_LEAST_ONE_KEY

    return end_key_value, follow_error

def get_json_from_request(request_link):
    request_content = requests.get(request_link)
    return str_to_json(request_content.text)

def get_self_ip():
    host_name = socket.gethostname()
    return socket.gethostbyname(host_name)

def test_json():
    json_content, error = read_json_from_file("test.json")  
    assert(error == constant.JSON_FILE_LOAD_SUCCES)

    json_content, error = read_json_from_file("test_b.json")  
    assert(error == constant.JSON_FILE_LOAD_FAIL)

    json_content, error = read_json_from_file("testa.json")  
    assert(error == constant.JSON_FILE_DOESNT_EXISTS)

    error = write_json_to_file("test.json", {"test" : 4})  
    assert(error == constant.JSON_FILE_DUMPS_SUCCES)

    error = write_json_to_file("test.json", {"test"})  
    assert(error == constant.JSON_FILE_DUMPS_FAIL)
def test_dict():
    test = {
        "a" : {
            "b" : {
                "c" : 1
            }
        },
        "d" : {
            "e" : 2,
            "f" : 3,
            "g" : {
                "h" : 4
            }
        }
    }

    key, error = follow_path_in_dict(test, "/")
    assert(error == constant.FOLLOW_PATH_PATH_MUST_HAVE_AT_LEAST_ONE_KEY)

    key, error = follow_path_in_dict(test, "/b/")
    assert(error == constant.FOLLOW_PATH_CANT_FIND_KEY)

    key, error = follow_path_in_dict(test, "/a/b/c/d/")
    assert(error == constant.FOLLOW_PATH_VALUE_ISNT_DICT)

    key, error = follow_path_in_dict(test, "/a/b/c/")
    assert(error == constant.FOLLOW_PATH_SUCCES)

    key, error = follow_path_in_dict(test, "/a/e/c")
    assert(error == constant.FOLLOW_PATH_CANT_FIND_KEY)