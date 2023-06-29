import requests
from serializers.auth_model import AuthResponse
from serializers.booking_model import BookingResponse

base_url = 'https://restful-booker.herokuapp.com'

def auth_token():
    url = base_url + '/auth'
    headers = {'Content-Type': 'application/json'}
    data = {
        'username': 'admin',
        'password': 'password123'
    }
    response = requests.post(url, headers=headers, json=data)
    response_model = AuthResponse(**response.json())
    return response_model.token


def create_booking(auth_token):
    url = base_url + '/booking'
    headers = {'Content-Type': 'application/json'}
    data = {
        'firstname': 'Vlad',
        'lastname': 'Grey',
        'totalprice': 987,
        'depositpaid': True,
        'bookingdates': {
            'checkin': '2023-01-01',
            'checkout': '2023-02-02'
        },
        'additionalneeds': 'UAI'
    }
    response = requests.post(url, headers=headers, json=data)
    response_model = BookingResponse(**response.json())
    return response_model.bookingid