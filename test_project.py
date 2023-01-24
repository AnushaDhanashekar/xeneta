import requests
from datetime import datetime
from main import db, Ports, Prices, Regions, connection, engine

ENDPOINT = "http://127.0.0.1:5000/rates?"
PARAMETERS = "date_from=2016-01-01&date_to=2016-01-2&origin=CNGGZ&destination=EETLL"

def test_can_call_endpoint():
    response = requests.get(
        "http://127.0.0.1:5000/rates?date_from=2016-01-01&date_to=2016-01-2&origin=CNGGZ&destination=EETLL")
    assert response.status_code == 200


def test_can_call_get_endpoint():
    payload = {
        "prices": [
            {
                "average_price": "1154.6666666666666667",
                "day": "2016-01-01"
            },
            {
                "average_price": "1154.6666666666666667",
                "day": "2016-01-02"
            }
        ]
    }

    get_task_response = get_task('2016-01-01', '2016-01-2', 'CNGGZ', 'EETLL')
    assert get_task_response.status_code == 200
    get_task_data = get_task_response.json()
    print(get_task_data)
    assert get_task_data["prices"][0]["average_price"] == payload["prices"][0]["average_price"]
    assert get_task_data["prices"][0]["day"] == payload["prices"][0]["day"]
    assert get_task_data["prices"][1]["average_price"] == payload["prices"][1]["average_price"]
    assert get_task_data["prices"][1]["day"] == payload["prices"][1]["day"]



def get_task(date_from, date_to, origin, destination):
    assert bool(datetime.strptime(date_from, "%Y-%m-%d")) == True
    assert bool(datetime.strptime(date_to, "%Y-%m-%d")) == True
    assert bool(date_from <= date_to) == True
    return requests.get(
        ENDPOINT + f"date_from={date_from}&date_to={date_to}&origin={origin}&destination={destination}")
