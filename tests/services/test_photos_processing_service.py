import pytest
from app.services.photos_processing_service import PhotosProcessingService
from tests.factories.file_factory import FileFactory
from werkzeug.datastructures import MultiDict


@pytest.fixture
def mock_cropping_service(mocker):
    mock = mocker.patch("app.services.cropping.vips_cropping_service.VipsCroppingService")
    mock.return_value.cropped_image_stream = b"fake-bytes"
    return mock


@pytest.fixture
def mock_cropping_service_dict(mocker, mock_cropping_service):
    dict = mocker.patch.dict(
        "app.services.photos_processing_service.PhotosProcessingService.CROP_SERVICES", {"vips": mock_cropping_service}
    )
    return dict


@pytest.fixture
def mock_files_multidict():
    def _factory(filenames=["file.jpg", "file2.jpg"]):
        files = [FileFactory(filename=name) for name in filenames]
        multidict = MultiDict({"images": files})
        return multidict

    return _factory


def test_processed_file_name_match_input(mock_cropping_service, mock_cropping_service_dict, mock_files_multidict):
    files = mock_files_multidict(["file1.jpg", "file2.jpg"])
    service = PhotosProcessingService(files, "vips")
    service()

    assert [f["filename"] for f in service.processed_files] == ["file1.jpg", "file2.jpg"]


def test_appends_cropped_image_stream_to_processed_files(
    mock_cropping_service, mock_cropping_service_dict, mock_files_multidict
):
    files = mock_files_multidict()
    service = PhotosProcessingService(files, "vips")
    service()

    assert all(f["io"] == b"fake-bytes" for f in service.processed_files)


def test_raises_value_error_for_invalid_crop_method(mock_cropping_service_dict, mock_files_multidict):
    files = mock_files_multidict()
    service = PhotosProcessingService(files, "invalid_method")

    with pytest.raises(PhotosProcessingService.ValueError) as e:
        service()

    assert str(e.value) == "No cropping service for method: invalid_method"
