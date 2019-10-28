#### THE STREAM FUNCTION BELOW IS NOT OURS, IT IS FROM A PYTHON PACKAGE CALLED STREAMY
#### WE COULDN'T GET IT TO INSTALL, SO WE COPIED IT HERE AND ARE GIVING CREDIT TO AUTHORS
#### LINK TO REPO: https://github.com/timedata-org/streamy


import re
import platform
import json

_IS_PY3 = platform.python_version() >= '3'
_STRING_TYPES = str if _IS_PY3  else (str, 'unicode')  # noqa: F821
_PARSE_EXCEPTIONS = platform.python_version() >= '3.4'
_MATCH_EXPECTING_EXCEPTION = re.compile(r'Expecting .*: .*char (\d+).*').match

def stream(fp, chunk_size=0, max_message_size=0, **kwds):
    """
    A function generating a stream of valid JSON objects.

    Args:
        fp: a file stream like you'd get from `open()` or `io.StringIO()`,
            or a string.
        json_lines: if true, each line holds at most one JSON expression.
        kwds: keywords to pass to json.load or json.loads.
    """
    def yield_chunks():
        while True:
            chunk = fp.read(chunk_size)
            if not chunk:
                return
            yield chunk

    if isinstance(fp, _STRING_TYPES):
        chunks = [fp]
    elif chunk_size:
        chunks = yield_chunks()
    else:
        chunks = fp

    decoder = json.JSONDecoder(**kwds)
    unread = ''
    for chunk in chunks:
        unread = ((unread + chunk) if unread else chunk).lstrip()
        if max_message_size and len(unread) > max_message_size:
            raise ValueError('Message size exceeded max_message_size')

        while unread:
            try:
                data, index = decoder.raw_decode(unread)
            except ValueError as e:
                if not _PARSE_EXCEPTIONS:
                    # In Python 2, we just don't get enough information in
                    # the exception to figure out if we're in case 2.
                    break
                match = _MATCH_EXPECTING_EXCEPTION(e.args[0])
                if match and int(match.group(1)) >= len(unread) - 2:
                    break
                if e.args[0].startswith('Unterminated string'):
                    break

                # We're in case 2.
                raise
            else:
                yield data
                unread = unread[index:].strip()

    if unread:
        raise ValueError('Extra text at end of stream')

