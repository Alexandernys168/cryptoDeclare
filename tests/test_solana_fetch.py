import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch

from data import fetch_transactions


class MockResponse:
    def __init__(self, data):
        self._data = data
    def raise_for_status(self):
        pass
    def json(self):
        return self._data


def mocked_post(url, json=None, timeout=10):
    method = json.get("method")
    if method == "getSignaturesForAddress":
        call = mocked_post.calls
        mocked_post.calls += 1
        if call == 0:
            batch = [{"signature": f"sig{i}"} for i in range(1000)]
        else:
            batch = [{"signature": "lastsig"}]
        return MockResponse({"result": batch})
    elif method == "getTransaction":
        sig = json["params"][0]
        return MockResponse({"result": {"signature": sig}})
    return MockResponse({"result": None})

mocked_post.calls = 0


def test_fetch_solana_transactions():
    with patch("requests.post", side_effect=mocked_post):
        with patch("time.sleep", return_value=None):
            txs = fetch_transactions("addr", "solana")
    assert len(txs) == 1001
    assert txs[0]["signature"] == "sig0"
    assert txs[-1]["signature"] == "lastsig"
