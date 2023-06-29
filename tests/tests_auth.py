import pytest
import requests
from pydantic import ValidationError
from serializers.auth_model import AuthRequestModel

#Тесты на создание токена

@pytest.mark.auth
@pytest.mark.parametrize('username, password, headers', [
    ('admin', 'password123', {"Content-Type": "application/json"}),  # Позитивные тесты с валидными значениями
    ('ad min', 'pass word123', {"Content-Type": "applica tion/js on"}),# Пробелы внутри валидных значений
    ('', '', {"Content-Type": "application/json"}),                  # Отсутсвие данных в теле запроса
    ( 1, 1, {"Content-Type": "application/json"}),                   # Числа в данных в теле запроса вместо сторки
    ( 'ЗLСOFjpYШоWЭrмAЯKВmWBцMJцzGтшPqшnDЙDзФГг'
      'иМCeпСghGёcTЕЪYHяёдУжЩЙжМdиЛGbГQfшIUГjWл'
      'MnЯCЗлЫЬcuюSЯкrхJЖSfsjХЦXЛКIТЗъGLЯУdFХрО'
      'ЖШоИVвТvBtШvУАKЫюЛWOeЖzЮГзRnyТВжcЫзеQiEp'
      'oтwUVхвГaиABдиCУULйrюЖoгСзЫZlgтVёIrHлкII'
      'TctHzШЖоМqмЫCЧяGтбсхBБЭёwkфVoKЙkщЮsУdЁэv'
      'меHЖЬTTXбJvЭCLDd', 'password123', {"Content-Type": "application/json"}), # Строка более 255 символов в поле username в теле запроса
    ( 'admin', 'ЗLСOFjpYШоWЭrмAЯKВmWBцMJцzGтшPqшnDЙDзФГг'
      'иМCeпСghGёcTЕЪYHяёдУжЩЙжМdиЛGbГQfшIUГjWл'
      'MnЯCЗлЫЬcuюSЯкrхJЖSfsjХЦXЛКIТЗъGLЯУdFХрО'
      'ЖШоИVвТvBtШvУАKЫюЛWOeЖzЮГзRnyТВжcЫзеQiEp'
      'oтwUVхвГaиABдиCУULйrюЖoгСзЫZlgтVёIrHлкII'
      'TctHzШЖоМqмЫCЧяGтбсхBБЭёwkфVoKЙkщЮsУdЁэv'
      'меHЖЬTTXбJvЭCLDd', {"Content-Type": "application/json"}),    # Строка более 255 символов в поле password теле запроса
    (  """№;"?@%صسغذئآ龍門大酒秋瑞<IMG src="#">') # ; -- ☺☻♥♦♣♠•◘""",
       'password123' {"Content-Type": "application/json"}),         # Строка специальных символов в поле username тела запроса
    (  'admin',"""№;"?@%صسغذئآ龍門大酒秋瑞<IMG src="#">') # ; -- ☺☻♥♦♣♠•◘""",
       {"Content-Type": "application/json"}),                       # Строка специальных символов в поле password тела запроса
    (  '<script>alert("Поле input уязвимо!")</script>',
       'password123' {"Content-Type": "application/json"}),         # XSS инъекции (JS) в поле username тела запроса
    (  'admin', '<script>alert("Поле input уязвимо!")</script>',
       {"Content-Type": "application/json"}),                       # XSS инъекции (JS) в поле password тела запроса
    ('dsaqwe', 'asd123', {"Content-Type": "application/json"}),     # Не верные данные в теле запроса
    ('admin', 'password123', None,                                   # Отсутсвие заголовка запроса
    ('admin', 'password123', {"Content-Type": ""}),                 # Незаполненный Content-Type заголовка запроса
    ('admin', 'password123', {"Content-Type": "text/html"}),        # Невалидный Content-Type заголовка запроса
    ('admin', 'password123', {"Content-Type": 1 }),                 # Число в Content-Type заголовка запроса вместо строки
    ( 'admin', 'password123',
      {"Content-Type": 'ЗLСOFjpYШоWЭrмAЯKВmWBцMJцzGтшPqшnDЙDзФГг'
      'иМCeпСghGёcTЕЪYHяёдУжЩЙжМdиЛGbГQfшIUГjWл'
      'MnЯCЗлЫЬcuюSЯкrхJЖSfsjХЦXЛКIТЗъGLЯУdFХрО'
      'ЖШоИVвТvBtШvУАKЫюЛWOeЖzЮГзRnyТВжcЫзеQiEp'
      'oтwUVхвГaиABдиCУULйrюЖoгСзЫZlgтVёIrHлкII'
      'TctHzШЖоМqмЫCЧяGтбсхBБЭёwkфVoKЙkщЮsУdЁэvмеHЖЬTTXбJvЭCLDd'}), # Строка более 255 символов в поле Content-Type заголовка запроса
    ( 'admin', 'password123',
      {"Content-Type": """№;"?@%صسغذئآ龍門大酒秋瑞<IMG src="#">') # ; -- ☺☻♥♦♣♠•◘"""}),
    # Строка специальных символов в поле Content-Type заголовка запроса
    ( 'admin', 'password123',
      {"Content-Type": '<script>alert("Поле input уязвимо!")</script>'})
    # XSS инъекции (JS) в поле Content-Type заголовка запроса
])
def test_auth_request(username, password, headers):
    url = "https://restful-booker.herokuapp.com/auth"

    try:
        data = AuthRequestModel(username=username, password=password)
    except ValidationError as e:
        if username == '' and password == '':
            assert str(e) == "1 validation error for AuthRequestModel\nusername\n  " \
                             "field required (type=value_error.missing)\npassword\n  " \
                             "field required (type=value_error.missing)"
        else:
            pytest.fail(f"Failed to validate request data: {e}")

    response = requests.post(url, headers=headers, json=data.dict())

    assert response.status_code == 200, f"Request failed with status code {response.status_code}"
    if "reason" in response.json() and response.json()["reason"] == "Bad credentials":
        assert "token" not in response.json(), "Response contains a token for invalid credentials"
    else:
        assert "token" in response.json(), "Response does not contain a token"
