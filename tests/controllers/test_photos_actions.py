from app.controllers.photos_actions import crop_photos
from tests.factories.file_factory import FileFactory
from unittest.mock import ANY
from flask import request
from werkzeug.datastructures import MultiDict
import pytest
import io


@pytest.fixture
def files():
    return MultiDict({"photos": []})


@pytest.fixture
def mock_photos_service(mocker):
    mock = mocker.patch("app.controllers.photos_actions.PhotosProcessingService")
    mock.return_value.processed_files = [
        FileFactory(filename="test_file_1.jpg"),
        FileFactory(filename="test_file_2.jpg"),
    ]
    return mock


@pytest.fixture
def mock_zip_service(mocker):
    mock = mocker.patch("app.controllers.photos_actions.ZipFilesService")
    mock.return_value.return_value = io.BytesIO(b"dummy zip content")
    return mock


def test_crop_photos_returns_zip_response(files, mock_photos_service, mock_zip_service):
    response, status_code = crop_photos(files)

    assert response.mimetype == "application/zip"
    assert status_code == 201


def test_crop_photos_passes_files_to_processing_service(mock_photos_service, mock_zip_service):
    crop_photos(files)
    mock_photos_service.assert_called_once_with(files, ANY)


def test_crop_photos_uses_default_crop_method(files, mock_photos_service, mock_zip_service):
    crop_photos(files)
    mock_photos_service.assert_called_once_with(ANY, "vips")


def test_crop_photos_uses_specified_crop_method(files, mock_photos_service, mock_zip_service):
    request.form = {"crop_method": "other method"}
    crop_photos(files)
    mock_photos_service.assert_called_once_with(ANY, "other method")


def test_crop_photos_passes_files_from_processing_service_to_zip_service(files, mock_photos_service, mock_zip_service):
    crop_photos(files)
    mock_zip_service.assert_called_once_with(mock_photos_service.return_value.processed_files)


def test_crop_photos_handles_value_error(files, mock_zip_service, mocker):
    from app.services.photos_processing_service import PhotosProcessingService

    mocker.patch(
        "app.controllers.photos_actions.PhotosProcessingService.__call__",
        side_effect=PhotosProcessingService.ValueError("Invalid crop method"),
    )

    response, status_code = crop_photos(files)
    assert status_code == 422
    assert response.json == {"error": "Invalid crop method"}
