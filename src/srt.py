import re

_CUE = re.compile(
    r"(?P<start>\d{2}:\d{2}:\d{2}),(?P<sm>\d{3})\s*-->\s*"
    r"(?P<end>\d{2}:\d{2}:\d{2}),(?P<em>\d{3})"
)


def _to_ms(hhmmss, millis):
    h, m, s = (int(x) for x in hhmmss.split(":"))
    return ((h * 60 + m) * 60 + s) * 1000 + int(millis)


def _fmt(ms):
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, milli = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{milli:03d}"


def parse(text):
    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.splitlines()
        if len(lines) < 2:
            continue
        match = _CUE.search(lines[1] if lines[0].strip().isdigit() else lines[0])
        if not match:
            continue
        body = lines[2:] if lines[0].strip().isdigit() else lines[1:]
        out.append({
            "index": int(lines[0]) if lines[0].strip().isdigit() else len(out) + 1,
            "start_ms": _to_ms(match["start"], match["sm"]),
            "end_ms": _to_ms(match["end"], match["em"]),
            "text": "\n".join(body),
        })
    return out


def shift(cues, offset_ms):
    """Shift every cue by ``offset_ms``.

    Raises ``ValueError`` if the shift would move any cue before 00:00:00;
    silently clamping the timeline would hide the data loss from operators.
    """
    shifted = []
    for cue in cues:
        start = cue["start_ms"] + offset_ms
        end = cue["end_ms"] + offset_ms
        if start < 0 or end < 0:
            raise ValueError(
                f"shift of {offset_ms} ms would move cue "
                f"{cue.get('index', '?')} before 00:00:00"
            )
        shifted.append(dict(cue, start_ms=start, end_ms=end))
    return shifted


def render(cues):
    blocks = []
    for i, c in enumerate(cues, 1):
        blocks.append(f"{i}\n{_fmt(c['start_ms'])} --> {_fmt(c['end_ms'])}\n{c['text']}")
    return "\n\n".join(blocks) + "\n"
