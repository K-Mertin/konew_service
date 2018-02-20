from flask import Blueprint

blueprint = Blueprint('hello', __name__)


@blueprint.route("/")
def hello():
    return "Hello World!"