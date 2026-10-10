# String Width Calculator

Determines the terminal column width of a string in a monospace font, accounting for wide East Asian glyphs and zero-width combining characters.

## Usage

```python
from string_width_calculator import width, visible_chars

print(width("hello"))            # 5
print(width("\u4e2d"))           # 2  (CJK ideograph)
print(width("e\u0301"))         # 1  (e + combining acute renders as one cell)
print(visible_chars("e\u0301")) # 1  (combining mark does not add a slot)
```

## Why this exists

Terminal layout code that assumes one byte or one code point equals one column breaks the moment it meets CJK text or accented characters built from combining marks. This library gives a correct column count using only the standard library, so it can be vendored or run inside a sandboxed container with no network access.

The trade-off is that `width` operates on Unicode code points, not grapheme clusters. Emoji ZWJ sequences (e.g. "family" built from multiple code points joined by `U+200D`) are counted as the sum of their visible constituent code points, not as one merged cluster. This keeps the implementation dependency-free and predictable; if you need grapheme-cluster-level width you need a heavier library with a full Unicode segmentation database.

## Edge cases you will hit

- **Tab (`\t`)** counts as 1 column, because terminals expand tabs to a variable width the calculator cannot know in advance. If you need tab expansion, expand first.
- **Variation selectors** (`U+FE0F` and `U+FE0E`) are treated as zero-width, matching how they render over the preceding base.
- **Bidirectional format controls** (`U+202A`–`U+202E`) are zero-width; they affect reading direction, not column count.
- **C1 control characters** (`U+0080`–`U+009F`) are counted as width 1, not hidden, because some terminals render them and we prefer not to silently drop characters the terminal might show.
