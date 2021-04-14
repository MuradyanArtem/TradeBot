import re
import os
import datetime

import requests
import flask
import flask_login
import flask_sqlalchemy
import flask_migrate
import sqlalchemy
import jsonschema


HTTP_TIMEOUT = 3


transaction = {
    "type": "object",
    "properties": {
        "from": {"type": "string", "maxLength": 3, "minimum": 0},
        "to": {"type": "string", "maxLength": 3, "minimum": 0},
        "amount": {"type": "number"},
    },
    "required": ["from", "to", "amount"],
}


signin = {
    "type": "object",
    "properties": {
        "username": {"type": "string", "format": "email"},
        "password": {"type": "string"},
    },
    "required": ["username", "password"],
}


signup = {
    "type": "object",
    "properties": {
        "username": {"type": "string", "format": "email"},
        "password": {"type": "string"},
        "repeat_password": {"type": "string"},
    },
    "required": ["username", "password", "repeat_password"],
}


class CurrencyNotFound(Exception):
    """raised when converter hasn't specified currency"""

    pass


class CurrencyApiError(Exception):
    """raised when http request to currency api failed"""

    pass


app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_NAME")
app.config["SECRET_KEY"] = os.getenv("SECRET")
db = flask_sqlalchemy.SQLAlchemy()
db.init_app(app)
migrate = flask_migrate.Migrate(app, db, render_as_batch=True)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


class User(flask_login.UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    wallet = db.relationship("Wallet", uselist=False, back_populates="user")


class Wallet(db.Model):
    __tablename__ = "wallet"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="wallet")


class Currency(db.Model):
    __tablename__ = "currency"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(3))
    amount = db.Column(db.Integer)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"))
    wallet = db.relationship("Wallet", backref="currencies")


class Converter:
    def __init__(self, token=None):
        self.base_url = "http://data.fixer.io/api/"
        self.token = token
        self.currencies = {}

        # TODO make cronjob to update currencies
        self.update_currencies()

    def update_currencies(self):
        try:
            r = requests.get(
                self.base_url + "latest",
                params={"access_key": self.token},
                timeout=HTTP_TIMEOUT,
            )
        except:
            raise CurrencyApiError
        self.currencies = r.json()

    def get_currency(self, name):
        try:
            currency = self.currencies.get("rates", {}).get(name)
        except KeyError:
            raise CurrencyNotFound
        return currency

    def convert(self, from_currency, to_currency, amount):
        return (
            amount / self.get_currency(from_currency) * self.get_currency(to_currency)
        )


converter = Converter(token=os.getenv("CURRENCY_TOKEN"))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/users/account", methods=["POST"])
def sign_up():
    try:
        data = flask.request.get_json()
        jsonschema.validate(data, signup)
    except (
        jsonschema.exceptions.ValidationError,
        jsonschema.exceptions.SchemaError,
    ) as err:
        app.logger.error(err)
        flask.abort(400)

    if data.get("password") != data.get("repeat_password"):
        app.logger.error("User not repeat password")
        flask.abort(400)

    try:
        user = User(email=data.get("username"), password=data.get("password"))
        user.wallet = Wallet()
        user.wallet.currencies = [Currency(code="USD", amount=1000)]
        db.session.add(user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as err:
        app.logger.error(err)
        flask.abort(400)

    flask_login.login_user(user)
    return flask.Response(status=201)


@app.route("/users/session", methods=["POST"])
def sign_in():
    try:
        data = flask.request.get_json()
        jsonschema.validate(data, signin)
    except (
        jsonschema.exceptions.ValidationError,
        jsonschema.exceptions.SchemaError,
    ) as err:
        app.logger.error(err)
        flask.abort(400)
    user = User.query.filter_by(email=data.get("username")).first()
    if not user:
        flask.abort(404)
    flask_login.login_user(user)
    return flask.Response(status=201)


@app.route("/users/session", methods=["DELETE"])
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.Response(status=200)


@app.route("/transactions", methods=["POST"])
@flask_login.login_required
def make_transaction():
    try:
        data = flask.request.get_json()
        jsonschema.validate(data, transaction)
    except (
        jsonschema.exceptions.ValidationError,
        jsonschema.exceptions.SchemaError,
    ) as err:
        app.logger.error(err)
        flask.abort(400)

    user = flask_login.current_user

    # TODO rework models. Delete iteration over List
    from_currency = [
        currency
        for currency in user.wallet.currencies
        if currency.code == data.get("from")
    ]
    if len(from_currency) == 0:
        app.logger.info("User can't make transaction")
        flask.abort(409)
    from_currency = from_currency[0]
    if from_currency.amount < data.get("amount"):
        app.logger.info("Not enough money to make transaction")
        flask.abort(409)
    from_currency.amount -= data.get("amount")

    to_currency = [
        currency
        for currency in user.wallet.currencies
        if currency.code == data.get("to")
    ]
    if len(to_currency) > 0:
        to_currency[0].amount += converter.convert(
            from_currency=data.get("from"),
            to_currency=data.get("to"),
            amount=data.get("amount"),
        )
    else:
        user.wallet.currencies.append(
            Currency(
                code=data.get("to"),
                amount=converter.convert(
                    from_currency=data.get("from"),
                    to_currency=data.get("to"),
                    amount=data.get("amount"),
                ),
            )
        )
    db.session.commit()
    return flask.Response(status=201)


@app.route("/users/wallet", methods=["GET"])
@flask_login.login_required
def get_currenies():
    return flask.jsonify(
        [
            {"amount": i.amount, "code": i.code}
            for i in flask_login.current_user.wallet.currencies
        ]
    )
