import jsonschema

from . import modules


class Application:
    def __init__(
        self,
        tc: modules.TradeClient,
        auth: modules.Auth,
        template: modules.Template,
        scheme: modules.Scheme
    ):
        self.__trade_client = tc
        self.__auth = auth
        self.__template = template
        self.__schema = scheme

    @property
    def usage(self):
        return self.__template.usage

    async def login(self, username: str, data: str):
        data = data.split(" ")
        if len(data) != 3:
            return self.__template.invalid_input

        form = {
            "username": data[1],
            "password": data[2],
        }
        try:
            jsonschema.validate(form, self.__schema.signin)
        except (
            jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError,
        ) as err:
            # TODO add json logging
            print(err)
            return self.__template.invalid_input

        answer = await self.__trade_client.login(form)
        if answer.get("status") != 201:
            return self.__template.bad_answer

        self.__auth.add_session(username, answer.get("cookie"))
        return self.__template.success_login

    async def register(self, username: str, data: str):
        data = data.split(" ")
        if len(data) != 4:
            return self.__template.invalid_input

        form = {"username": data[1], "password": data[2], "repeat_password": data[3]}
        try:
            jsonschema.validate(form, self.__schema.signup)
        except (
            jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError,
        ) as err:
            print(err)
            return self.__template.invalid_input

        answer = await self.__trade_client.register(form)
        if answer.get("status") != 201:
            return self.__template.bad_answer

        self.__auth.add_session(username, answer.get("cookie"))
        return self.__template.success_register

    async def logout(self, username: str):
        if not self.__auth.check_session(username):
            return self.__template.login_required

        answer = await self.__trade_client.logout(self.__auth.get_cookie(username))
        if answer.get("status") != 200:
            return self.__template.bad_answer

        self.__auth.delete_session(username)
        return self.__template.success_logout

    async def get_wallet(self, username: str):
        if not self.__auth.check_session(username):
            return self.__template.login_required

        answer = await self.__trade_client.get_wallet(self.__auth.get_cookie(username))
        if answer.get("status") != 200:
            return self.__template.bad_answer

        body = answer.get("body")
        all_wallets = ""
        for el in body:
            all_wallets += self.__template.success_wallet.format(
                el.get("code"), el.get("amount")
            )
        return all_wallets

    async def transaction(self, username: str, data: str):
        if not self.__auth.check_session(username):
            return self.__template.login_required

        data = data.split(" ")
        if len(data) != 4:
            return self.__template.invalid_input

        try:
            form = {
                "from": data[1],
                "to": data[2],
                "amount": int(data[3]),
            }
        except ValueError:
            return self.__template.invalid_input
        try:
            jsonschema.validate(form, self.__schema.transaction)
        except (
            jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError,
        ) as err:
            print(err)
            return self.__template.invalid_input

        form["from"] = modules.sanitize_code(form["from"])
        form["to"] = modules.sanitize_code(form["to"])

        answer = await self.__trade_client.transaction(
            form, self.__auth.get_cookie(username)
        )
        if answer.get("status") != 201:
            return self.__template.bad_answer

        return self.__template.success_transaction
