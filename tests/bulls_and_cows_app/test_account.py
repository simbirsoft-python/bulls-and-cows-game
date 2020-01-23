from flask import url_for


def test_auth(client, user1):
    target_url = url_for('bulls_and_cows.AccountView:login')
    data = {
        'email': user1.email,
        'password': '123456'
    }
    response = client.post(target_url, data=data)
    # Если возвращается код 200, значит произошла какая-то ошибка, а если
    # выполняется переадресация, значит авторизация прошла успешно
    assert 302 == response.status_code
