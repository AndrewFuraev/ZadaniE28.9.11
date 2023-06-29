import pytest
import requests
from api.api import auth_token, create_booking

# Тесты требующие получения токена

@pytest.mark.xfail
@pytest.mark.required_token
@pytest.mark.parametrize(
    'auth_token, create_booking, content_type, expected_status',
    [(auth_token(), create_booking(auth_token), 'application/json', 201),      #Валидные значения токена, пути и данных content_type
     ("", create_booking(auth_token), 'application/json', 403),                # Пустое значения токена
     ('asd324sda', create_booking(auth_token), 'application/json', 403),       # Неверное значение токена
     (2 , create_booking(auth_token), 'application/json', 400),                # Число в значение токена
     ('ЗLСOFjpYШоWЭrмAЯKВmWBцMJцzGтшPqшnDЙDзФГг'
      'иМCeпСghGёcTЕЪYHяёдУжЩЙжМdиЛGbГQfшIUГjWл'
      'MnЯCЗлЫЬcuюSЯкrхJЖSfsjХЦXЛКIТЗъGLЯУdFХрО'
      'ЖШоИVвТvBtШvУАKЫюЛWOeЖzЮГзRnyТВжcЫзеQiEp'
      'oтwUVхвГaиABдиCУULйrюЖoгСзЫZlgтVёIrHлкII'
      'TctHzШЖоМqмЫCЧяGтбсхBБЭёwkфVoKЙkщЮsУdЁэv'
      'меHЖЬTTXбJvЭCLDd', create_booking(auth_token), 'application/json', 400),  # Строка более 255 символов в значение токена
     (""""№;"?@%صسغذئآ龍門大酒秋瑞<IMG src="#">') # ; -- ☺☻♥♦♣♠•◘""", create_booking(auth_token),
      'application/json', 400),                # Строка специальных символов в значение токена
     ('<script>alert("Поле input уязвимо!")</script>', create_booking(auth_token), 'application/json', 400),
     # XSS инъекции (JS) в значение токена
     (auth_token(), -1, 'application/json', 400),                            # Отрицательное значение booking_id
     (auth_token(), 2555555, 'application/json', 403),                       # Неверное значение booking_id
     (auth_token(), "", 'application/json', 400),                            # Пустое значение booking_id
     (auth_token(), "1", 'application/json', 400),                           # Строка в  значение booking_id
     (auth_token(), 'ЗLСOFjpYШоWЭrмAЯKВmWBцMJцzGтшPqшnDЙDзФГг'
      'иМCeпСghGёcTЕЪYHяёдУжЩЙжМdиЛGbГQfшIUГjWл'
      'MnЯCЗлЫЬcuюSЯкrхJЖSfsjХЦXЛКIТЗъGLЯУdFХрО'
      'ЖШоИVвТvBtШvУАKЫюЛWOeЖzЮГзRnyТВжcЫзеQiEp'
      'oтwUVхвГaиABдиCУULйrюЖoгСзЫZlgтVёIrHлкII'
      'TctHzШЖоМqмЫCЧяGтбсхBБЭёwkфVoKЙkщЮsУdЁэv'
      'меHЖЬTTXбJvЭCLDd', 'application/json', 400),                           # Строка более 255 символов в  значение booking_id
     (auth_token(), """№;"?@%صسغذئآ龍門大酒秋瑞<IMG src="#">') # ; -- ☺☻♥♦♣♠•◘""", 'application/json', 400),
     # Строка специальных символов значение booking_id
     (auth_token(), '<script>alert("Поле input уязвимо!")</script>', 'application/json', 400),
     # XSS инъекции (JS) в  значение booking_id
     (auth_token(), 2147483648, 'application/json', 400),               #Ввод максимального целочисленного значения +1 в  значение booking_id
     (auth_token(), create_booking(auth_token), 'text/html', 415),     # Неверный content_type
     (auth_token(), create_booking(auth_token), None, 400),            # Отсутсвие content_type
     (auth_token(), create_booking(auth_token), '', 400),              # Пустое згачение в content_type
     (auth_token(), create_booking(auth_token), 1, 400),               # Число в content_type
     (auth_token(), create_booking(auth_token), 'ЗLСOFjpYШоWЭrмAЯKВmWBцMJцzGтшPqшnDЙDзФГг'
      'иМCeпСghGёcTЕЪYHяёдУжЩЙжМdиЛGbГQfшIUГjWл'
      'MnЯCЗлЫЬcuюSЯкrхJЖSfsjХЦXЛКIТЗъGLЯУdFХрО'
      'ЖШоИVвТvBtШvУАKЫюЛWOeЖzЮГзRnyТВжcЫзеQiEp'
      'oтwUVхвГaиABдиCУULйrюЖoгСзЫZlgтVёIrHлкII'
      'TctHzШЖоМqмЫCЧяGтбсхBБЭёwkфVoKЙkщЮsУdЁэv'
      'меHЖЬTTXбJvЭCLDd', 400),                                        # Строка более 255 символов в content_type
     (auth_token(), create_booking(auth_token),
      """№;"?@%صسغذئآ龍門大酒秋瑞<IMG src="#">') # ; -- ☺☻♥♦♣♠•◘""", 400), # Строка специальных символов в content_type
     (auth_token(), create_booking(auth_token),
      '<script>alert("Поле input уязвимо!")</script>', 400),     #  XSS инъекции (JS)в content_type
     ])
def test_delete_booking(auth_token, create_booking, content_type, expected_status):

    url = f'https://restful-booker.herokuapp.com/booking/{create_booking}'
    headers = {
        'Content-Type': f'{content_type}',
        'Cookie': f'token={auth_token}'
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 201:
        assert response.status_code == expected_status, f'Delete booking request failed with status code {response.status_code}'
        assert response.text == 'Created', 'Delete booking ответ должен содержать "Created"'
    elif response.status_code == 403:
        assert response.status_code == expected_status, f'Delete booking request failed with status code {response.status_code}'
        assert response.text == 'Forbidden', 'Delete booking ответ должен содержать "Created"'
    elif response.status_code == 400:
        assert response.status_code == expected_status, f'Delete booking request failed with status code {response.status_code}'
        assert response.text == 'Bad Request', 'Delete booking ответ должен содержать "Created"'
    elif response.status_code == 415:
        assert response.status_code == expected_status, f'Delete booking request failed with status code {response.status_code}'
        assert response.text == 'Unsupported content-type', 'Delete booking ответ должен содержать "Created"'