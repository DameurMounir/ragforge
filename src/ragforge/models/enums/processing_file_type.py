from enum import Enum


class ProcessingFileType(str, Enum):
    TXT = '.txt'
    PDF = '.pdf'