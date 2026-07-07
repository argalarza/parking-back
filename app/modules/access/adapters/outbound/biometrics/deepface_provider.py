from deepface import DeepFace

from app.application.errors import ValidationError


class DeepFaceEmbeddingProvider:
    def extract_embedding(self, image_path: str) -> list[float]:
        representations = DeepFace.represent(
            img_path=image_path,
            model_name="Facenet",
            enforce_detection=True,
            detector_backend="mtcnn",
        )

        if not representations:
            raise ValidationError("No se pudo extraer un embedding facial de la imagen.")

        embedding = representations[0].get("embedding")
        if embedding is None:
            raise ValidationError("DeepFace no devolvio un vector facial valido.")

        return [float(value) for value in embedding]
