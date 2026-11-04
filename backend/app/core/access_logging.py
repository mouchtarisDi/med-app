"""Narrow privacy protection for Uvicorn's patient-list access records."""

import logging
import re


_PATIENT_LIST = re.compile(r"/clinics/0*[1-9][0-9]*/patients")
_ACCESS_MESSAGE = '%s - "%s %s HTTP/%s" %d'


class PatientListAccessFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Pinned Uvicorn supplies five positional args. Do not format unknown
        # records to classify them: msg or args may themselves contain a URL.
        # Suppress only that record if its structure cannot be safely recognized.
        if not isinstance(record.args, tuple) or len(record.args) != 5:
            return False
        client, method, target, version, status = record.args
        if not (
            isinstance(client, str)
            and isinstance(method, str) and re.fullmatch(r"[A-Z]+", method)
            and isinstance(target, str) and target.startswith("/")
            and isinstance(version, str) and re.fullmatch(r"[0-9]+\.[0-9]+", version)
            and type(status) is int and 100 <= status <= 599
        ):
            return False

        path = target.partition("?")[0]
        if method == "GET" and _PATIENT_LIST.fullmatch(path):
            target = path
        # Canonicalize even a changed template: sensitive URL text must not
        # survive in msg while AccessFormatter independently reads the args.
        record.msg = _ACCESS_MESSAGE
        record.args = (client, method, target, version, status)
        for field in ("message", "color_message"):
            record.__dict__.pop(field, None)
        # Access records have no exception payload in the verified protocol.
        record.exc_info = None
        record.exc_text = None
        record.stack_info = None
        return True


def configure_access_log_privacy() -> None:
    """Keep existing handlers/formatters and avoid duplicate filter installs."""
    logger = logging.getLogger("uvicorn.access")
    if not any(isinstance(item, PatientListAccessFilter) for item in logger.filters):
        logger.addFilter(PatientListAccessFilter())
