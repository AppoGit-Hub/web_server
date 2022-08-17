from fastapi import FastAPI
from datetime import datetime
import uvicorn
import socket
import utils
import constant
import followers_stats

followers_stats_files_cache = {}

class StatManager:
    def __init__(self):
        _today = datetime.today()
        self.stats_last_time_refresh = {
            "average" : _today,
            "total" : _today,
            "time" : _today
        }

    def does_stats_need_refesh(self, stat_type):
        api_permanent_file, error = utils.read_json_from_file(f"{constant.DATA_FOLDER}/{constant.API_PERMANENT_DATA_FILENAME}")
        last_time_got_followers_stats = datetime.today()
        if error == constant.JSON_FILE_LOAD_SUCCES:
            last_time_got_followers_stats = utils.str_to_datetime(api_permanent_file["last_time_got_followers_stats"])
        else:
            print(f"Couldnt load api_permanent_file. Error : {error}")
        return datetime.today() - last_time_got_followers_stats > constant.TIME_DELTA_REFRESH

    def update_last_time_accesed(self, stat_type):
        need_refresh = self.does_stats_need_refesh(stat_type)
        #self.stats_last_time_refresh[stat_type] = datetime.today()
        if need_refresh:
            followers_stats.create_follower_stats()
        return need_refresh 


def create_error(error_type):
    return {
        "error_type" : error_type,
        "error_description" : constant.ERROR_TYPE_DESCRIPTION[error_type]
    }

def get_file_cache(filename):
    file_content = followers_stats_files_cache.get(filename, 0)
    if file_content == 0:
        json_content, error = utils.read_json_from_file(filename)
        if error == constant.JSON_FILE_LOAD_SUCCES:
            file_content = json_content
    return file_content

def get_self_ip():
    host_name = socket.gethostname()
    return socket.gethostbyname(host_name)

app = FastAPI()
stat_manager = StatManager()

def get_stats(type, stat_name):
    filename_of_stat, error = utils.follow_path_in_dict(constant.STATS_TYPES_WITH_NAMES, f"{type}/{stat_name}")
    json_content = {}
    if error == constant.FOLLOW_PATH_SUCCES:
        json_content = get_file_cache(f"{constant.DATA_FOLDER}/{filename_of_stat}")
    return json_content, error

@app.get("/refresh")
def need_refresh(type) -> bool:
    return stat_manager.update_last_time_accesed(type)

@app.get("/stats")
def get_average_graphs(type, stat):
    json_content, error = get_stats(type, stat)
    if error != constant.FOLLOW_PATH_SUCCES:
        json_content = create_error(constant.ERROR_TYPE_COULDNT_FIND_STAT_TYPE)
    return json_content

@app.on_event("startup")
def on_startup():
    permanent_data, error = utils.read_json_from_file(f"{constant.DATA_FOLDER}/{constant.DATA_SAVE_FILENAME}")
    if error == constant.JSON_FILE_LOAD_SUCCES:
        stat_manager.stats_last_time_refresh = {
            "average" : utils.str_to_datetime(permanent_data["average"]),
            "total" : utils.str_to_datetime(permanent_data["total"]),
            "time" : utils.str_to_datetime(permanent_data["time"])
        }
    else:
        print(f"Error while load permanent_data : {error}")

@app.on_event("shutdown")
def on_shutdown():
    error = utils.write_json_to_file(f"{constant.DATA_FOLDER}/{constant.DATA_SAVE_FILENAME}", {
        "average" : str(stat_manager.stats_last_time_refresh["average"]),
        "total" : str(stat_manager.stats_last_time_refresh["total"]),
        "time" : str(stat_manager.stats_last_time_refresh["time"]),
    })
    print(f"writing json error: {error}")

if __name__ == "__main__":
    uvicorn.run("web_backend:app", host=f"{get_self_ip()}", port=constant.API_PORT, log_level="info")