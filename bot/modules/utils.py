def sanitize_url(url: str) -> str:
    if len(url) == 0:
        return ""

    if url[-1] != "/":
        return url + "/"
    return url


def sanitize_code(code: str) -> str:
    return code.upper()
