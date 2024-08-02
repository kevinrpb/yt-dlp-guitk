import humanize


def bytes_to_human(bytes: int) -> str:
    return humanize.naturalsize(bytes, binary=True)
