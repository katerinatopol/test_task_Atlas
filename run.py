import ssl
import pymongo
import requests

my_client = pymongo.MongoClient(
        'mongodb+srv://TestUser:59808sKWRTn@cluster0.i3w5f.mongodb.net/DB_jokes?retryWrites=true&w=majority',
        ssl_cert_reqs=ssl.CERT_NONE)

my_db = my_client.DB_jokes
users = my_db.users
jokes = my_db.jokes


def add_user(user_name, password):
    """
    Функция добавляет данные нового пользователя в базу данных
    """
    new_user = {
        "username": user_name,
        "password": password,
        "jokes": [],
    }
    users.insert_one(new_user)
    return new_user


def add_joke(content):
    """
    Функция добавляет данные новой шутки в базу данных.
    """
    new_joke = {"content": content}
    jokes.insert_one(new_joke)
    return new_joke


def start():
    """
    Функция перенаправляет пользователя на функции регистрации и регистрации
    """
    while True:
        user_input = input('Введите +, если вы новый пользователь.\nНажмите Enter, если уже зарегистрированы: ')
        if user_input == '+':
            return sign_up()
        elif user_input == '':
            return sign_in()


def sign_in():
    """
     Функция запрашивает логин от пользователя и проверяет наличие данных в базе,
     в случае если пользователь ранее регистрировался, запрашивает пароль и
     сверяет его с данными из базы.
     Возвращает данные пользователя.
    """
    user_login = input('Введите имя пользователя: ')
    user_data = users.find_one({
        "username": user_login
    })
    if not user_data:
        print('Вы не зарегистрированы')
        return start()
    while True:
        user_password = input('Введите пароль: ')
        if user_password != user_data['password']:
            print('Неверный пароль, попробуйте еще раз.')
        else:
            print('Успешный вход')
            break
    return user_data


def sign_up():
    """
    Функция запрашивает логин пользователя, в случае отсутствия его данных
    в базе - запрашивает пароль, вызывает функцию add_user()
    """
    while True:
        user_login = input('Введите имя пользователя: ')
        if users.find_one({'username': user_login}):
            print('Такой пользователь уже существует')
        else:
            break
    while True:
        user_password = input('Введите пароль: ')
        check_password = input('Повторите пароль: ')
        if user_password == check_password:
            break
        print('Попробуйте еще раз')
    new_user = add_user(user_login, user_password)
    print('Вы успешно зарегистрированы.')
    return new_user


def add_jokes(user, variant):
    """
    Функция в зависимости от переданного параметра, либо предоставляет пользователю ввод
    текста шутки, либо запрашивает текст с удаленного ресурса.
    Полученный текст передает в функцию add_joke().
    Id шутки, сгенерированный при добавлении в базу данных, добавляется в массив поля
    jokes для текущего пользователя.
    """
    if variant == '1':
        joke_content = input('Введите текст шутки: ')
    elif variant == '2':
        res = requests.get('https://geek-jokes.sameerkumar.website/api')
        joke_content = res.text
    new_joke = add_joke(joke_content)
    users.update_one(
        {"_id": user['_id']},
        {"$push": {"jokes": new_joke['_id']}}
    )
    print(f'Ваша новая шутка:\n{joke_content}')


def check_access(user, id_joke):
    """
    Функция выполняет поиск шутки по ID, проверяя массив jokes для
    текущего пользователя.
    Возвращает результат поиска в виде Boolean.
    """
    is_check = False
    for i in user['jokes']:
        if str(i) == id_joke:
            id_joke = i
            is_check = True
            break
    if not is_check:
        id_joke = None
        print('Шутка вам не доступна')
    return is_check, id_joke


def render_user_jokes(user):
    """
    Функция отображает все шутки, доступные пользователю.
    """
    list_jokes = user['jokes']
    for num, i in enumerate(list_jokes, 1):
        joke = jokes.find_one({"_id": i})
        print(f"{num}. {joke['content']} (ID: {joke['_id']})")


def render_joke(id_joke):
    """
    Функция отображает текст шутки по переданному ID
    """
    joke = jokes.find_one({"_id": id_joke})
    print(joke['content'])


def update_joke(id_joke, variant):
    """
    Функция изменяет текст шутки в базе данных, новый текст вводится
    пользователем либо запрашивается с удаленного ресурса.
    """
    if variant == '1':
        joke_content = input('Введите текст шутки: ')
    elif variant == '2':
        res = requests.get('https://geek-jokes.sameerkumar.website/api')
        joke_content = res.text
    jokes.update_one(
        {"_id": id_joke},
        {"$set": {"content": joke_content}}
    )
    print(f'Ваша новая шутка:\n{joke_content}')


def remove_joke(user, id_joke):
    """
    Функция удаляет шутку пользователя из базы jokes и из массива jokes
    текущего пользователя.
    """
    jokes.delete_one({"_id": id_joke})
    users.update_one(
        {"_id": user['_id']},
        {"$pull": {"jokes": id_joke}}
    )
    print('Шутка удалена')


if __name__ == '__main__':
    active_user = start()

    user_choice = input('*******\n'
                        'Выберите, что вы хотите сделать\n'
                        '1. Добавить шутку\n'
                        '2. Смотреть свои шутки\n'
                        '3. Смотреть шутку по ID\n'
                        '4. Обновить текст моей шутки\n'
                        '5. Удалить мою шутку\n'
                        'Введите ответ: ')
    if user_choice == '1':
        user_answer = input('Вы хотите самостоятельно написать шутку(1) или автоматически сгенерировать(2): ')
        add_jokes(active_user, user_answer)
    elif user_choice == '2':
        render_user_jokes(active_user)
    elif user_choice == '3':
        input_id = input('Введите ID шутки: ')
        check, correct_id = check_access(active_user, input_id)
        if check:
            render_joke(correct_id)
    elif user_choice == '4':
        input_id = input('Введите ID шутки: ')
        check, correct_id = check_access(active_user, input_id)
        if check:
            render_joke(correct_id)
            user_answer = input('Вы хотите самостоятельно написать шутку(1) или автоматически сгенерировать(2): ')
            update_joke(correct_id, user_answer)
    elif user_choice == '5':
        input_id = input('Введите ID шутки: ')
        check, correct_id = check_access(active_user, input_id)
        if check:
            render_joke(correct_id)
            user_answer = input('Подтвердите удаление шутки, введите DEL: ')
            if user_answer == 'DEL':
                remove_joke(active_user, correct_id)
