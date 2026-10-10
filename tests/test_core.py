import unittest

from string_width_calculator import width, visible_chars


class TestWidth(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(width(""), 0)

    def test_ascii(self):
        self.assertEqual(width("hello"), 5)

    def test_ascii_visible_chars(self):
        self.assertEqual(visible_chars("hello"), 5)

    def test_tab_counts_as_one(self):
        self.assertEqual(width("a\tb"), 3)

    def test_combining_acute_is_zero(self):
        # "e" + U+0301 COMBINING ACUTE ACCENT renders as a single accented glyph
        self.assertEqual(width("e\u0301"), 1)
        self.assertEqual(visible_chars("e\u0301"), 1)

    def test_zwj_is_zero_width(self):
        # U+200D ZERO WIDTH JOINER — not merged into a single cluster here
        self.assertEqual(width("a\u200Db"), 2)
        self.assertEqual(visible_chars("a\u200Db"), 2)

    def test_hangul_syllable_is_wide(self):
        # U+AC00 is a Hangul syllable; East_Asian_Width=W
        self.assertEqual(width("\uac00"), 2)

    def test_cjk_ideograph_is_wide(self):
        # U+4E2D (middle) — a CJK Unified Ideograph
        self.assertEqual(width("\u4e2d"), 2)

    def test_fullwidth_letter_is_wide(self):
        # U+FF21 FULLWIDTH LATIN CAPITAL LETTER A
        self.assertEqual(width("\uff21"), 2)

    def test_halfwidth_katakana_is_narrow(self):
        # U+FF61 HALFWIDTH KATAKANA MIDDLE DOT — East_Asian_Width=Hs (treated narrow)
        self.assertEqual(width("\uff61"), 1)

    def test_mixed_string(self):
        # "A" (1) + CJK (2) + combining mark (0) + "B" (1)
        s = "A\u4e2d\u0301B"
        self.assertEqual(width(s), 4)
        self.assertEqual(visible_chars(s), 3)

    def test_variation_selector_is_zero(self):
        # U+FE0F is category Mn, treated as zero-width
        self.assertEqual(width("a\ufe0f"), 1)
        self.assertEqual(visible_chars("a\ufe0f"), 1)

    def test_control_chars_c1_are_zero(self):
        # U+009B is category Cc — not in our zero set (Mn/Me/Cf), so it counts as 1.
        # We document that only Mn/Me/Cf (plus the bidi format controls we list)
        # are treated as zero. Cc control characters are rare in text; the choice
        # is: count them rather than risk hiding something a terminal shows.
        self.assertEqual(width("\u009b"), 1)

    def test_multiple_combining_marks(self):
        s = "e\u0301\u0308"  # e + acute + diaeresis
        self.assertEqual(width(s), 1)
        self.assertEqual(visible_chars(s), 1)


if __name__ == "__main__":
    unittest.main()
