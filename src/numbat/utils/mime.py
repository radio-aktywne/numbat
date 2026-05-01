import re
from collections.abc import Mapping
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from numbat.models.base import datamodel


class MimeTypeValidationError(ValueError):
    """Raised when a MIME type is invalid."""

    def __init__(self, value: str | None = None) -> None:
        super().__init__(f"Invalid MIME type{f': {value}' if value else ''}.")


@datamodel
class MimeType:
    """MIME type."""

    type: str
    subtype: str
    parameters: Mapping[str, str]

    @property
    def fulltype(self) -> str:
        """Return the full MIME type."""
        return f"{self.type}/{self.subtype}"

    @staticmethod
    def __get_pydantic_core_schema__(
        source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        string_validation_schema = core_schema.no_info_after_validator_function(
            MimeType.parse, handler(str)
        )

        instance_validation_schema = core_schema.is_instance_schema(MimeType)

        serialization_schema = core_schema.plain_serializer_function_ser_schema(
            MimeType.serialize
        )

        return core_schema.json_or_python_schema(
            json_schema=string_validation_schema,
            python_schema=core_schema.union_schema(
                [instance_validation_schema, string_validation_schema]
            ),
            serialization=serialization_schema,
        )

    def __str__(self) -> str:
        """Return the MIME type as a string."""
        return self.serialize()

    @staticmethod
    def parse(value: Any) -> "MimeType":
        """Parse a MIME type."""
        parser = MimeTypeParser()
        return parser.parse(value)

    def serialize(self) -> str:
        """Serialize the MIME type."""
        serializer = MimeTypeSerializer()
        return serializer.serialize(self)


class MimeTypeParser:
    """Parser for MIME types."""

    class PATTERNS:
        FULL = re.compile(
            r"^\s*(?P<type>[\w!#$%&'*+\-.\^_`{|}~]+)\s*/\s*(?P<subtype>[\w!#$%&'*+\-.\^_`{|}~]+)(?P<parameters>(?:\s*;\s*[\w!#$%&'*+\-.\^_`{|}~]+\s*=\s*(?:[\w!#$%&'*+\-.\^_`{|}~]+|\"(?:[^\"\\]|\\.)*\")\s*(?:\((?:[^()\\]|\\.)*\))?)*)\s*$"
        )
        PARAMETER = re.compile(
            r"\s*;\s*(?P<key>[\w!#$%&'*+\-.\^_`{|}~]+)\s*=\s*(?:(?P<value>[\w!#$%&'*+\-.\^_`{|}~]+)|\"(?P<quoted>(?:[^\"\\]|\\.)*)\")\s*(?:\((?:[^()\\]|\\.)*\))?"
        )
        ESCAPED = re.compile(r"\\(?P<escaped>.)")

    def parse(self, value: Any) -> MimeType:
        """Parse a MIME type."""
        try:
            value = str(value)
        except Exception as e:
            raise MimeTypeValidationError from e

        if not (fullmatch := self.PATTERNS.FULL.fullmatch(value)):
            raise MimeTypeValidationError(value)

        parameters = {
            match["key"].lower(): match["value"]
            or self.PATTERNS.ESCAPED.sub(r"\g<escaped>", match["quoted"])
            for match in self.PATTERNS.PARAMETER.finditer(fullmatch["parameters"])
        }

        return MimeType(
            type=fullmatch["type"].lower(),
            subtype=fullmatch["subtype"].lower(),
            parameters=parameters,
        )

    def __call__(self, value: Any) -> MimeType:
        """Parse a MIME type."""
        return self.parse(value)


class MimeTypeSerializer:
    """Serializer for MIME types."""

    class PATTERNS:
        UNQUOTED = re.compile(r"^[\w!#$%&'*+\-.\^_`{|}~]+$")
        ESCAPE = re.compile(r"(?P<escape>[\"\\])")

    def serialize(self, value: MimeType) -> str:
        """Serialize a MIME type."""
        parameters = [
            f"{k}={v}"
            if self.PATTERNS.UNQUOTED.fullmatch(v)
            else f'{k}="{self.PATTERNS.ESCAPE.sub(r"\\\g<escape>", v)}"'
            for k, v in value.parameters.items()
        ]

        return f"{value.type}/{value.subtype}{'; '.join(['', *parameters]) if parameters else ''}"

    def __call__(self, value: MimeType) -> str:
        """Serialize a MIME type."""
        return self.serialize(value)
