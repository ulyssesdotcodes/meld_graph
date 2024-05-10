from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
import time
import json
import csv
import os, sys
import types

from util import convert_csv_to_json, convert_json_to_csv, parse_path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import scripts.new_patient_pipeline.new_pt_pipeline

hostName = "0.0.0.0"
serverPort = 8080



class MyServer(BaseHTTPRequestHandler):
    def do_POST(self):
        parsed_path = parse_path(self.path)
        if self.path == "/bids-config":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            pd = post_data.decode("utf-8")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps({"message": "updated config"}), "utf-8"));
        elif parsed_path["path"] == "demographic-information":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            pd = post_data.decode("utf-8")
            convert_json_to_csv(pd, "/data/demographics_file_{}.csv".format(parsed_path["query"]["name"][0]))
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps({"message": "success"}), "utf-8"));
        else:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps({"message": "not post endpoint 2"}), "utf-8"));

    def do_GET(self):
        parsed_path = parse_path(self.path)
        if self.path == "/test":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps({"message": "didn\'t run test 2"}), "utf-8"))
        elif parsed_path["path"] == "demographic-information":
            json_data = convert_csv_to_json("/data/demographics_file_{}.csv".format(parsed_path["query"]["name"][0]))
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json_data, "utf-8"));
        elif parsed_path["path"] == "compute-harmo":
            args = types.SimpleNamespace(
                id = "sub-test001",
                list_ids=None,
                harmo_code = parsed_path["query"]["name"][0],
                fastsurfer=False,
                parallelise=False,
                demographic_file = "/data/demographics_file_{}.csv".format(parsed_path["query"]["name"][0]),
                harmo_only=False,
                skip_feature_extraction=False,
                no_nifti=False,
                no_report=False,
                debug_mode=False
            )
            scripts.new_patient_pipeline.new_pt_pipeline.run(args)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps({"message": "success"}), "utf-8"));
        else:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps({"message": "not test endpoint 2"}), "utf-8"));

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
