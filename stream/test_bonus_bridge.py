import json

from stream.bonus_bridge import write_landing


def test_write_landing_writes_raw_json_lines(tmp_path):
    records = [{"order_id": "R-1", "amount": "500", "currency": "INR"}]

    path = write_landing(records, "run-1", str(tmp_path))

    assert path.name == "rabbitmq__run-1.jsonl"
    assert json.loads(path.read_text(encoding="utf-8").splitlines()[0]) == records[0]
