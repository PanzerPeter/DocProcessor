class DocProcessorError(Exception):
    """Base exception for all DocProcessor errors."""


class ExtractionError(DocProcessorError):
    """Raised when text extraction fails."""


class CategorizationError(DocProcessorError):
    """Raised when AI categorization fails or returns unparseable output."""


class UnsupportedFileTypeError(DocProcessorError):
    """Raised when the input file type is not supported."""


class EmptyDocumentError(DocProcessorError):
    """Raised when no text could be extracted from the document."""
