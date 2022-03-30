import json, pytest
from app import app as flask_app


@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client() 

def test_add_transactions(client):
    url = "http://localhost:5000/add_transactions"

    data = {"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z"}
    response = client.post(url, json = data)
    assert response.status_code == 200

    data = { "payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z" }
    response = client.post(url, json = data)
    assert response.status_code == 200

    data = {"payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z"}
    response = client.post(url, json = data)
    assert response.status_code == 200
    
    data = {"payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z"}
    response = client.post(url, json = data)
    assert response.status_code == 200
    
    data = {"payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z"}
    response = client.post(url, json = data)
    assert response.status_code == 200


def test_spend_points(client):
    url = "http://localhost:5000/spend_points"
    data = { "points": -3}
    response = client.post(url, json = data)
    assert response.status_code == 400
    
    data = { "points": 30000}
    response = client.post(url, json = data)
    assert response.status_code == 400

    data = { "points": 5000 }
    response = client.post(url, json = data)
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert data == [{ "payer": "DANNON", "points": -100 },
                    { "payer": "UNILEVER", "points": -200 },
                    { "payer": "MILLER COORS", "points": -4700 }]
    


def test_check_balance(client):
    url = "http://localhost:5000/check_balance"
    response = client.get(url)
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert data == {"DANNON": 1000, "UNILEVER": 0, "MILLER COORS": 5300}









# with app.test_client() as c:
#     response = c.get('/some/path/that/exists')
#     self.assertEquals(response.status_code, 200)



# if __name__ == '__main__':
#     unittest.main()
