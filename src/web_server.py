from matplotlib import pyplot
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import requests
import json
import utils
import constant

get_cache = {}

def get_image_from_file(image_path):
    with open(image_path, "rb") as file:
        image_content_list = file.readlines()  
        image_content = bytes()
        for image_byte in image_content_list:
            image_content += image_byte
    return image_content

def get_file_from_cache(filepath, file_type=constant.FILE_TYPE_TEXT):
    file_content = get_cache.get(filepath, 0)
    if file_content == 0:
        if file_type == constant.FILE_TYPE_TEXT: 
            with open(filepath, "r") as file:
                file_content = ''.join(file.readlines())    
        elif file_type == constant.FILE_TYPE_IMAGE:
            file_content = get_image_from_file(filepath)
        get_cache.update({filepath : file_content})
    return file_content

def create_graph_from_request(type, stat, filename, title):
    response = get_stat_from_api(type, stat)
    if response.status_code == 200:
        json_content, error = utils.str_to_json(response.text)
        if error == constant.JSON_FILE_LOAD_SUCCES:
            create_graph(json_content, utils.get_path_for_resource(filename), title)
        else:
            print(f"Couldnt str_to_json {filename}")
    else:
        print("Couldnt create graph")

def create_graph_from_request_simple(type, stat):
    create_graph_from_request(type, stat, f"{type}_{stat}.png", f"Average {stat} of the last 7 days")

def get_stat_from_api(type, stat):
    return requests.get(f"http://{constant.API_ADDRESS}/stats?type={type}&stat={stat}")

def get_refresh_from_api(type):
    return requests.get(f"http://{constant.API_ADDRESS}/refresh?type={type}")

def create_graph(dict, filename, title):
    like_label = dict.keys()
    likes_values = dict.values()
    
    pyplot.figure(figsize=(16, 9))

    pyplot.bar(like_label, likes_values)
    pyplot.xticks(range(len(like_label)), rotation='vertical')
    pyplot.title(title)

    pyplot.savefig(filename, bbox_inches='tight', dpi=100)

class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith(".png"):            
            image_content = get_file_from_cache(utils.get_path_for_resource(self.path[1:]), constant.FILE_TYPE_IMAGE)
            
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            self.wfile.write(image_content)
        
        elif self.path.endswith(".ico"):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            with open(utils.get_path_for_resource("favicon.ico"), "rb") as file:
                image_content_list = file.readlines()  
                image_content = bytes()
                for image_byte in image_content_list:
                    image_content += image_byte
            self.wfile.write(bytes(image_content))

        else:
            start_time = time.perf_counter()

            main_content = get_file_from_cache(utils.get_path_for_resource("index.html"))
            page_code = 200

            if self.path == "/":
                extra_page = "Select stats to view"
            elif self.path == "/average":
                extra_page = get_file_from_cache(utils.get_path_for_resource("average.html"))
                need_refresh = get_refresh_from_api("average")
                need_refresh = json.loads(need_refresh.text)
                if need_refresh:                
                    create_graph_from_request_simple("average", "like")
                    create_graph_from_request_simple("average", "quote")
                    create_graph_from_request_simple("average", "reply")
                    create_graph_from_request_simple("average", "retweet")
            elif self.path == "/total":
                extra_page = get_file_from_cache(utils.get_path_for_resource("total.html"))
                need_refresh = get_refresh_from_api("total")
                need_refresh = json.loads(need_refresh.text)
                if need_refresh:
                    create_graph_from_request_simple("total", "like")
                    create_graph_from_request_simple("total", "quote")
                    create_graph_from_request_simple("total", "reply")
                    create_graph_from_request_simple("total", "retweet")
                    create_graph_from_request_simple("total", "tweet")               
            elif self.path == "/time":
                extra_page = get_file_from_cache(utils.get_path_for_resource("time.html"))
                need_refresh = get_refresh_from_api("time")
                need_refresh = json.loads(need_refresh.text)                
                if need_refresh:
                    create_graph_from_request("time", "hour", "hour_create_at.png", "Hour tweets creation time of the last 7 days")
                    create_graph_from_request("time", "day", "day_create_at.png", "Day tweets creation time of the last 7 days")
            else:
                extra_page = get_file_from_cache(utils.get_path_for_resource("page_not_found.html"))
                page_code = 204

            finish_time = time.perf_counter()
            delta_time = finish_time - start_time

            page_content = bytes(main_content % (delta_time, extra_page), "UTF-8")

            self.send_response(page_code)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            self.wfile.write(page_content)

def main():
    web_server = HTTPServer((constant.HOST_IP, constant.HOST_PORT), WebServer)
    print(f"Server started http://{constant.HOST_IP}:{constant.HOST_PORT}")
    
    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass

    web_server.server_close()
    print("Server stopped.")

if __name__ == "__main__":        
    #cProfile.run("main()", sort="cumtime")
    main()