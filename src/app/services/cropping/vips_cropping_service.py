import io
import pyvips
from typing import IO
from app.services.cropping.cropping_service_base import CroppingService


class VipsCroppingService(CroppingService):
    def __init__(self, file):
        self._image_stream = file.stream
        self._filename = file.filename
        self._cropped_image = None
        self._cropped_image_stream = None

    def __call__(self) -> bool:
        self._crop_image(0.75)
        self._convert_image_to_stream()
        return True

    @property
    def cropped_image_stream(self) -> IO[bytes]:
        if self._cropped_image_stream is None:
            raise ValueError("Cropped image stream is not set. Call _convert_image_to_stream() first.")
        return self._cropped_image_stream

    def _get_image(self):
        if not hasattr(self, "_image"):
            image_bytes = self._image_stream.read()
            self._image = pyvips.Image.new_from_buffer(image_bytes, "")
        return self._image

    def _crop_image(self, scale: float) -> pyvips.Image:
        new_width = int(self._get_image().width * scale)
        new_height = int(self._get_image().height * scale)

        self._cropped_image = self._get_image().smartcrop(new_width, new_height)
        return self._cropped_image

    def _convert_image_to_stream(self) -> IO[bytes]:
        if self._cropped_image is None:
            raise ValueError("Cropped image is not set. Call _crop_image() first.")
        format = self._get_format()
        self._cropped_image_stream = io.BytesIO(self._cropped_image.write_to_buffer(format))
        return self._cropped_image_stream

    def _get_format(self) -> str:
        format = self._filename.split(".")[-1]
        return f".{format}" if format else ".jpg"
