import json
from urllib.parse import urlparse, parse_qs
import csv


def parse_path(path: str):
    query_index = path.find("?")
    query_index = query_index if query_index >= 0 else len(path)
    non_query_path = path[1:query_index]
    return {
        "path": non_query_path,
        "segments": non_query_path.split("/"),
        "query": parse_qs(path[query_index + 1:])
    }

def convert_csv_to_json(csv_path: str):
    with open(csv_path) as csv_file:
        json_output = []
        csv_content = csv.DictReader(csv_file)
        for row in csv_content:
            json_output.append(row)
        return json.dumps(json_output)

def convert_json_to_csv(json_str: str, csv_path: str):
    json_content = json.loads(json_str)
    with open(csv_path, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(json_content[0].keys())
        for row in json_content:
            csv_writer.writerow(row.values())

