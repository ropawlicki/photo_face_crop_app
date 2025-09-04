from typing import List
from app.schemas.photos import ProcessedFileDict
from app.services.cropping.cropping_service_base import CroppingService
from app.services.cropping.vips_cropping_service import VipsCroppingService
from werkzeug.datastructures import FileStorage, MultiDict


class PhotosProcessingService:
    AVAILABLE_CROP_METHODS = ("vips",)

    class ServiceError(Exception):
        pass

    class ValueError(ServiceError):
        pass

    def __init__(self, files: MultiDict[str, FileStorage], crop_method: str):
        self.files: MultiDict[str, FileStorage] = files
        self.processed_files: List[ProcessedFileDict] = []
        self.crop_method: str = crop_method
        self._verify_crop_method()

    def __call__(self) -> None:
        for key, files in self.files.lists():
            for file in files:
                cropping_service = self._initialize_cropping_service(file)
                cropping_service()
                file_dict: ProcessedFileDict = {
                    "io": cropping_service.cropped_image_stream,
                    "filename": file.filename if file.filename is not None else "",
                }
                self.processed_files.append(file_dict)

    def _verify_crop_method(self) -> None:
        if self.crop_method not in self.AVAILABLE_CROP_METHODS:
            raise self.ValueError(
                f"Unknown crop method: {self.crop_method}. Available: {', '.join(str(m) for m in self.AVAILABLE_CROP_METHODS)}"
            )

    def _initialize_cropping_service(self, file) -> CroppingService:
        if self.crop_method == "vips":
            return VipsCroppingService(file)
