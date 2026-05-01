from numbat.utils.mime import MimeType


class ContentTypeChecker:
    """Utility class for checking supported content types."""

    SUPPORTED = frozenset({"audio/ogg"})

    def check(self, content_type: MimeType) -> bool:
        """Check if the given content type is supported."""
        return content_type.fulltype in self.SUPPORTED
