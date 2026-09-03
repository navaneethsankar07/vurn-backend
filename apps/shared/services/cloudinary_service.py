import cloudinary.uploader

class CloudinaryService:

    @staticmethod
    def upload(
        file,
        *,
        folder: str,
    ) -> str:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="image",
        )

        return result["secure_url"]
