from __future__ import annotations

import unicodedata
from functools import lru_cache


@lru_cache(maxsize=8192)
def _is_wide(cp: int) -> bool:
    """Return True if the code point is East Asian Wide or Fullwidth.

    Why a cache: width() is typically called per-character across large strings,
    and unicodedata.east_asian_width involves several dict lookups internally.
    Memoising on the code point (a small int) keeps repeated text cheap.
    """
    try:
        return unicodedata.east_asian_width(chr(cp)) in ("W", "F")
    except ValueError:
        # Unassigned code points exist in the Unicode database. Treat them
        # as narrow rather than crashing — width() must never raise on input
        # the operating system can legitimately pass us.
        return False


@lru_cache(maxsize=4096)
def _is_zero(cp: int) -> bool:
    """Return True if the code point is a zero-width combiner.

    This covers Unicode general categories Mn (nonspacing mark), Me (enclosing
    mark), Cf (format) minus the three format characters that are visible in a
    terminal: TAB, and the two bidirectional controls that some terminals
    render as a blank cell. We deliberately exclude ZWJ (U+200D) here even
    though it is category Cf, because terminals generally do not render a cell
    for it and it is used to join emoji — which we are not handling.
    """
    if cp == 0x09:  # TAB — visible as spacing in a terminal
        return False
    if cp in (0x202A, 0x202B, 0x202C, 0x202D, 0x202E):
        # Bidirectional formatting controls. Some renderers treat these as a
        # visible cell; we choose to treat them as zero-width because in a
        # well-formed monospace layout they affect direction, not column count.
        return True
    try:
        return unicodedata.category(chr(cp)) in ("Mn", "Me", "Cf")
    except ValueError:
        return False


def visible_chars(s: str) -> int:
    """Count the number of visible *character slots* in `s`.

    A base character counts as one slot; a combining mark that follows it
    does not add a slot because it renders over the base. Emoji joined by
    ZWJ sequences are not merged here — each constituent code point is
    considered its own slot — because the brief asks for monospace column
    width, not grapheme-cluster width.
    """
    count = 0
    for ch in s:
        if not _is_zero(ord(ch)):
            count += 1
    return count


def width(s: str) -> int:
    """Return the terminal column width of `s` in a monospace font.

    Rules:
      - East Asian Wide and Fullwidth code points count as 2 columns.
      - Zero-width characters (combining marks, format controls, ZWJ) count 0.
      - Everything else counts as 1.

    The function operates on code points, not grapheme clusters. That is a
    deliberate simplification documented in the README: merging ZWJ emoji
    and regional-indicator flag pairs would require a full UCD grapheme
    segmentation pass, which is out of scope for a zero-dependency terminal
    width calculator.
    """
    total = 0
    for ch in s:
        cp = ord(ch)
        if _is_zero(cp):
            continue
        total += 2 if _is_wide(cp) else 1
    return total
