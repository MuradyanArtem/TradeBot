# TODO better templates
class Template:
    @property
    def usage(self):
        return (
            "ТрейдБот\n\n"
            "/transaction USD RUB 100 (купить рубли за 100 долларов)\n"
            "/login <login> <password> (авторизоваться)\n"
            "/register <login> <password> <repeat_password> (зарегистрироваться)\n"
            "/logout (выйти из аккаунта)\n"
            "/wallet (показать текущий счёт)"
        )

    @property
    def login_required(self):
        return "Необходимо авторизоваться"

    @property
    def invalid_input(self):
        return "Команда введена неправильно"

    # TODO return error to client
    @property
    def bad_answer(self):
        return "На сервере что-то пошло не так"

    @property
    def success_register(self):
        return "Регистрация прошла успешно"

    @property
    def success_login(self):
        return "Авторизация прошла успешно"

    @property
    def success_logout(self):
        return "Вы вышли из профиля"

    @property
    def success_wallet(self):
        return "Валюта: {}\nКолличество: {}\n\n"

    @property
    def success_transaction(self):
        return "Транзакция выполнена"
