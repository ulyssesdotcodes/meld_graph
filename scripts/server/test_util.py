import json
from util import convert_csv_to_json, parse_path


def test_path():
  parsed = parse_path("/xyz/abc?l=hi")
  print(parsed["query"])
  assert parsed["path"] == "xyz/abc"
  assert parsed["segments"][0] == "xyz"
  assert parsed["segments"][1] == "abc"
  assert parsed["query"]["l"][0] == "hi"

  parsed = parse_path("/xyz/abc")
  assert parsed["path"] == "xyz/abc"


def test_csv_to_json():
    json_test_str = convert_csv_to_json("test-data/test.csv")
    json_test = json.loads(json_test_str)
    assert json_test[0]["ID"] == "sub-test001"
    assert json_test[0]["Sex"] == '1'
    assert json_test[1]["ID"] == "sub-test002"
    assert json_test[1]["Sex"] == '0'
