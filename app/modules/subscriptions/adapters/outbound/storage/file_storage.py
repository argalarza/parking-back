from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from app.application.errors import ValidationError


class LocalReceiptStorage:
    _allowed_content_types = {"application/pdf", "image/jpeg", "image/png"}
    _allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png"}

    def __init__(self, upload_dir: str = "app/uploads/receipts", max_size_bytes: int = 5 * 1024 * 1024) -> None:
        self._upload_dir = Path(upload_dir)
        self._max_size_bytes = max_size_bytes

    def save(self, filename: str, content_type: str | None, file: BinaryIO) -> str:
        suffix = Path(filename or "").suffix.lower()
        if suffix not in self._allowed_extensions:
            raise ValidationError("El comprobante debe ser PDF, JPG o PNG.")
        if content_type not in self._allowed_content_types:
            raise ValidationError("El tipo de archivo del comprobante no es permitido.")

        self._upload_dir.mkdir(parents=True, exist_ok=True)
        destination = self._upload_dir / f"{uuid4()}{suffix}"

        size = 0
        try:
            with destination.open("wb") as output:
                while True:
                    chunk = file.read(1024 * 1024)
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > self._max_size_bytes:
                        output.close()
                        self.delete(str(destination))
                        raise ValidationError("El comprobante excede el tamano maximo permitido.")
                    output.write(chunk)
        except OSError as exc:
            self.delete(str(destination))
            raise ValidationError("No se pudo guardar el comprobante.") from exc

        return str(destination)

    def delete(self, path: str) -> None:
        try:
            Path(path).unlink(missing_ok=True)
        except OSError:
            return None
