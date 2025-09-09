# mypy: disable-error-code=misc

from flask import Blueprint, request, Response
from typing import Tuple
from werkzeug.datastructures import MultiDict, FileStorage
from app.controllers.photos_actions import crop_photos

main = Blueprint("main", __name__, url_prefix="/")
photos = Blueprint("photos", __name__, url_prefix="/photos")


@main.route("/")
def healthcheck() -> tuple[str, int]:
    return "App is running!", 200


@photos.route("/crop", methods=["POST"])
def crop_photos_route() -> Tuple[Response, int]:
    files: MultiDict[str, FileStorage] = request.files
    return crop_photos(files)
