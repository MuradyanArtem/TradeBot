# TODO store sessions in external storage
class Auth:
    def __init__(self) -> None:
        self.__sessions = {}

    def check_session(self, username: str) -> bool:
        if not self.__sessions.get(username):
            return False
        return True

    def get_cookie(self, username: str) -> str:
        return self.__sessions[username]

    def add_session(self, username: str, cookie: str) -> None:
        self.__sessions[username] = cookie

    def delete_session(self, username) -> None:
        del self.__sessions[username]
