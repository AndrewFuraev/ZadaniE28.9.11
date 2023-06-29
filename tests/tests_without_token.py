import pytest
import requests
from pydantic import ValidationError
from serializers.booking_model import BookingResponseModel, CreateBookingRequest, BookingResponse

# Тесты не требующие токена
# Обращаю внимание что в API-документации запрос GET возвращает ID как строку, а запрос POST возвращает ID как number,
# что само по себе баг, по этому реализована проверка ID cоответсвенно документации по разному в каждом запросе

@pytest.mark.without_token
@pytest.mark.parametrize('booking_id, expected_status, headers', [
    ('1', 200, {"Accept": "application/json"}),     # Валидные значения
    ('257', 404, {"Accept": "application/json"}),   # Не верное значение booking_id
    ('', 400, {"Accept": "application/json"}),      # Пустое поле booking_id
    (1, 400, {"Accept": "application/json"}),        # Число в booking_id
    ('ЗLСOFjpYШоWЭrмAЯKВmWBцMJцzGтшPqшnDЙDзФГг'
      'иМCeпСghGёcTЕЪYHяёдУжЩЙжМdиЛGbГQfшIUГjWл'
      'MnЯCЗлЫЬcuюSЯкrхJЖSfsjХЦXЛКIТЗъGLЯУdFХрО'
      'ЖШоИVвТvBtШvУАKЫюЛWOeЖzЮГзRnyТВжcЫзеQiEp'
      'oтwUVхвГaиABдиCУULйrюЖoгСзЫZlgтVёIrHлкII'
      'TctHzШЖоМqмЫCЧяGтбсхBБЭёwkфVoKЙkщЮsУdЁэv'
      'меHЖЬTTXбJvЭCLDd', 400, {"Accept": "application/json"}),    #  Строка более 255 символов в booking_id
    ("""№;"?@%صسغذئآ龍門大酒秋瑞<IMG src="#">') # ; -- ☺☻♥♦♣♠•◘""",
     400, {"Accept": "application/json"}),  # Строка специальных символов в booking_id
    ('<script>alert("Поле input уязвимо!")</script>',
     400, {"Accept": "application/json"}),  # XSS инъекции (JS)  в booking_id
    ('1', 400, {"Accept": ""}),                       # Пустое значение Accept
    ('1', 415, {"Accept": "text/html"}),                       # Неверный Accept
    ('1', 400, {"Accept": 1}),                       #  Число в значении Accept
    ('1', 400, {"Accept": 'ЗLСOFjpYШоWЭrмAЯKВmWBцMJцzGтшPqшnDЙDзФГг'
      'иМCeпСghGёcTЕЪYHяёдУжЩЙжМdиЛGbГQfшIUГjWл'
      'MnЯCЗлЫЬcuюSЯкrхJЖSfsjХЦXЛКIТЗъGLЯУdFХрО'
      'ЖШоИVвТvBtШvУАKЫюЛWOeЖzЮГзRnyТВжcЫзеQiEp'
      'oтwUVхвГaиABдиCУULйrюЖoгСзЫZlgтVёIrHлкII'
      'TctHzШЖоМqмЫCЧяGтбсхBБЭёwkфVoKЙkщЮsУdЁэv'
      'меHЖЬTTXбJvЭCLDd'}),                       #  Строка более 255 символов в значении Accept
    ('1', 400, {"Accept": """№;"?@%صسغذئآ龍門大酒秋瑞<IMG src="#">') # ; -- ☺☻♥♦♣♠•◘"""}),
    #  Строка специальных символов в значении Accept
    ('1', 400, {"Accept": '<script>alert("Поле input уязвимо!")</script>'}),
    #  XSS инъекции (JS) в значении Accept
    ('1', 400, None)                                  # Отсутсвует Accept
])
def test_get_booking(booking_id, expected_status, headers):
    url = f"https://restful-booker.herokuapp.com/booking/{booking_id}"

    response = requests.get(url, headers=headers)

    assert response.status_code == expected_status, f"Request failed with status code {response.status_code}"

    if expected_status == 200:
        try:
            data = response.json()
            booking = BookingResponseModel(**data)
        except (ValidationError, TypeError) as e:
            pytest.fail(f"Failed to validate booking response data: {e}")

        assert booking.firstname != '', "Имя клиента совершившего бронирование отсутствует или невероное"
        assert booking.lastname != '', "Фамилия клиента совершившего бронирование отсутсвуе или неверное"
        assert booking.totalprice >= 0, "Полная сумма бронирования не может быть меньше или ровна нулю"
        assert isinstance(booking.depositpaid, bool), "Присутвие залога должен быть boolean"
        assert isinstance(booking.bookingdates, dict), "Даты заезда и выезда должны быть словарем"
        assert "checkin" in booking.bookingdates and isinstance(booking.bookingdates["checkin"], str), \
            "Неправильная дата заезда или отсутвует"
        assert "checkout" in booking.bookingdates and isinstance(booking.bookingdates["checkout"], str), \
            "Неправильная дата выезда или отсутвует"
        assert isinstance(booking.additionalneeds, str), \
            "Пожелания клиента неправильные или отсутвует"



@pytest.mark.xfail
@pytest.mark.without_token
@pytest.mark.parametrize('headers, request_body, expected_status', [
    ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
        "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
        "additionalneeds": "UAI"}, 200),          # Валидные значения
    (None, {"firstname": "Jim", "lastname": "Brown", "totalprice": 111, "depositpaid": True,
            "bookingdates": {"checkin": "2018-01-01", "checkout": "2019-01-01"},
            "additionalneeds": "Breakfast"}, 400),  # Отсутсвие заголовка запроса
   ({"Content-Type": "text/html", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 415),          # Неверный Content-Type
   ({"Content-Type": "", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),          # Пустой Content-Type
   ({"Content-Type": 1, "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),          # Число в Content-Type
   ({"Content-Type": 'ЗLСOFjpYШоWЭrмAЯKВmWBцMJцzGтшPqшnDЙDзФГг'
      'иМCeпСghGёcTЕЪYHяёдУжЩЙжМdиЛGbГQfшIUГjWл'
      'MnЯCЗлЫЬcuюSЯкrхJЖSfsjХЦXЛКIТЗъGLЯУdFХрО'
      'ЖШоИVвТvBtШvУАKЫюЛWOeЖzЮГзRnyТВжcЫзеQiEp'
      'oтwUVхвГaиABдиCУULйrюЖoгСзЫZlgтVёIrHлкII'
      'TctHzШЖоМqмЫCЧяGтбсхBБЭёwkфVoKЙkщЮsУdЁэv'
      'меHЖЬTTXбJvЭCLDd', "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),          # Строка более 255 символов в Content-Type
   ({"Content-Type": """№;"?@%صسغذئآ龍門大酒秋瑞<IMG src="#">') # ; -- ☺☻♥♦♣♠•◘""", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),          # Строка специальных символов в Content-Type
   ({"Content-Type": '<script>alert("Поле input уязвимо!")</script>', "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),          # XSS инъекции (JS) в Content-Type
   ({"Content-Type": "application/json", "Accept": "text/html"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 415),          # Неверный Accept
   ({"Content-Type": "application/json", "Accept": ""},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),           # Пустой Accept
   ({"Content-Type": "application/json", "Accept": 1},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),           # Число в Accept
   ({"Content-Type": "application/json", "Accept": 'ЗLСOFjpYШоWЭrмAЯKВmWBцMJцzGтшPqшnDЙDзФГг'
      'иМCeпСghGёcTЕЪYHяёдУжЩЙжМdиЛGbГQfшIUГjWл'
      'MnЯCЗлЫЬcuюSЯкrхJЖSfsjХЦXЛКIТЗъGLЯУdFХрО'
      'ЖШоИVвТvBtШvУАKЫюЛWOeЖzЮГзRnyТВжcЫзеQiEp'
      'oтwUVхвГaиABдиCУULйrюЖoгСзЫZlgтVёIrHлкII'
      'TctHzШЖоМqмЫCЧяGтбсхBБЭёwkфVoKЙkщЮsУdЁэv'
      'меHЖЬTTXбJvЭCLDd'},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),          # Строка более 255 символов в Accept
   ({"Content-Type": "application/json", "Accept":  """№;"?@%صسغذئآ龍門大酒秋瑞<IMG src="#">') # ; -- ☺☻♥♦♣♠•◘"""},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),          # Строка специальных символов в Accept
   ({"Content-Type": "application/json", "Accept": '<script>alert("Поле input уязвимо!")</script>'},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),          # XSS инъекции (JS) в Accept
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),  # Пустой firstname
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": 1, "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),  # Число в firstname
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": 'ЗLСOFjpYШоWЭrмAЯKВmWBцMJцzGтшPqшnDЙDзФГг'
                                                    'иМCeпСghGёcTЕЪYHяёдУжЩЙжМdиЛGbГQfшIUГjWл'
                                                    'MnЯCЗлЫЬcuюSЯкrхJЖSfsjХЦXЛКIТЗъGLЯУdFХрО'
                                                    'ЖШоИVвТvBtШvУАKЫюЛWOeЖzЮГзRnyТВжcЫзеQiEp'
                                                    'oтwUVхвГaиABдиCУULйrюЖoгСзЫZlgтVёIrHлкII'
                                                    'TctHzШЖоМqмЫCЧяGтбсхBБЭёwkфVoKЙkщЮsУdЁэv'
                                                    'меHЖЬTTXбJvЭCLDd', "lastname": "Grey",
      "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),  # Строка более 255 в firstname
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": """№;"?@%صسغذئآ龍門大酒秋瑞<IMG src="#">') # ; -- ☺☻♥♦♣♠•◘""", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),  # Строка специальных символов firstname
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": '<script>alert("Поле input уязвимо!")</script>', "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),  # XSS инъекции (JS) в firstname
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),  # Пустой lastname
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": 1, "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),  # Число в lastname
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": 'ЗLСOFjpYШоWЭrмAЯKВmWBцMJцzGтшPqшnDЙDзФГг'
                   'иМCeпСghGёcTЕЪYHяёдУжЩЙжМdиЛGbГQfшIUГjWл'
                   'MnЯCЗлЫЬcuюSЯкrхJЖSfsjХЦXЛКIТЗъGLЯУdFХрО'
                   'ЖШоИVвТvBtШvУАKЫюЛWOeЖzЮГзRnyТВжcЫзеQiEp'
                   'oтwUVхвГaиABдиCУULйrюЖoгСзЫZlgтVёIrHлкII'
                   'TctHzШЖоМqмЫCЧяGтбсхBБЭёwkфVoKЙkщЮsУdЁэv'
                   'меHЖЬTTXбJvЭCLDd',
      "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),  # Строка более 255 в lastname
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": """№;"?@%صسغذئآ龍門大酒秋瑞<IMG src="#">') # ; -- ☺☻♥♦♣♠•◘""", "totalprice": 987,
      "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),  # Строка специальных символов lastname
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": '<script>alert("Поле input уязвимо!")</script>', "totalprice": 987,
      "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),  # XSS инъекции (JS) в lastname
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": "", "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),  # Пустой totalprice
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 2147483648, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),  # Ввод максимального целочисленного значения +1 в totalprice
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": "1", "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),  # Строка в totalprice
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": """№;"?@%صسغذئآ龍門大酒秋瑞<IMG src="#">') # ; -- ☺☻♥♦♣♠•◘""",
      "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),  # Строка специальных символов в totalprice
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey" , "totalprice": '<script>alert("Поле input уязвимо!")</script>',
      "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),  # XSS инъекции (JS) в totalprice
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": False,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": "UAI"}, 400),  # False в depositpaid
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {},
      "additionalneeds": "UAI"}, 400),  # Пустой bookingdates
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": ("checkin:2023-01-01", "checkout:2023-02-02"),
      "additionalneeds": "UAI"}, 400),  # Список в bookingdates
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": 2023,
      "additionalneeds": "UAI"}, 400),  # Число в bookingdates
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": "checkin:2023-01-01, checkout:2023-02-02",
      "additionalneeds": "UAI"}, 400),  # Строка в bookingdates
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": ""}, 400),  # Пустой additionalneeds
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": 1}, 400),  # Число в additionalneeds
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey" ,
      "totalprice": 987, "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": 'ЗLСOFjpYШоWЭrмAЯKВmWBцMJцzGтшPqшnDЙDзФГг'
                   'иМCeпСghGёcTЕЪYHяёдУжЩЙжМdиЛGbГQfшIUГjWл'
                   'MnЯCЗлЫЬcuюSЯкrхJЖSfsjХЦXЛКIТЗъGLЯУdFХрО'
                   'ЖШоИVвТvBtШvУАKЫюЛWOeЖzЮГзRnyТВжcЫзеQiEp'
                   'oтwUVхвГaиABдиCУULйrюЖoгСзЫZlgтVёIrHлкII'
                   'TctHzШЖоМqмЫCЧяGтбсхBБЭёwkфVoKЙkщЮsУdЁэv'
                   'меHЖЬTTXбJvЭCLDd'}, 400),  # Строка более 255 символов в additionalneeds
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987,
      "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": """№;"?@%صسغذئآ龍門大酒秋瑞<IMG src="#">') # ; -- ☺☻♥♦♣♠•◘"""}, 400),  # Строка специальных символов в additionalneeds
   ({"Content-Type": "application/json", "Accept": "application/json"},
     {"firstname": "Vlad", "lastname": "Grey", "totalprice": 987,
      "depositpaid": True,
      "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-02-02"},
      "additionalneeds": '<script>alert("Поле input уязвимо!")</script>'}, 400),  # XSS инъекции (JS) в additionalneeds
])
def test_create_booking(headers, request_body, expected_status):
    url = "https://restful-booker.herokuapp.com/booking"

    try:
        request_data = CreateBookingRequest(**request_body)
    except ValidationError as e:
        pytest.fail(f"Failed to validate request data: {e}")

    response = requests.post(url, headers=headers, json=request_data.dict())

    assert response.status_code == expected_status, f"Request failed with status code {response.status_code}"

    if expected_status == 200:
        try:
            response_data = response.json()
            booking_response = BookingResponse(**response_data)
        except (ValidationError, TypeError) as e:
            pytest.fail(f"Failed to validate booking response data: {e}")

        assert booking_response.bookingid is not None and isinstance(booking_response.bookingid, int), \
            "ID бронирования отсутсвует или неверное"
        assert isinstance(booking_response.booking, CreateBookingRequest), \
            "Данные бронирования отсутсвуют или неточные"
        booking = booking_response.booking
        assert booking.firstname == request_data.firstname, "Имя клиента совершившего бронирование отсутствует или неверное"
        assert booking.lastname == request_data.lastname, "Фамилия клиента совершившего бронирование отсутсвуе или неверная"
        assert booking.totalprice == request_data.totalprice, "Полная сумма бронирования отсутствует или неверная"
        assert booking.depositpaid == request_data.depositpaid, "Залог отсутствует или неверный"
        assert booking.bookingdates.dict() == request_data.bookingdates.dict(), "Даты заезда и выезда отсутствуют или неверные"
        assert booking.additionalneeds == request_data.additionalneeds, "Пожелания гостя отсутствуют или неверные"