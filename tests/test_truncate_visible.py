"""Unit tests for `truncate_visible()` and the width of `box_row()` rows."""

import contextlib
import io
import unittest

import cyber_search
import cyber_tools
import scifi_hud

MODULES = (cyber_tools, cyber_search, scifi_hud)


class TruncateVisibleTest(unittest.TestCase):
    def each_module(self):
        for module in MODULES:
            with self.subTest(module=module.__name__):
                yield module

    def test_text_that_fits_is_returned_unchanged(self):
        for m in self.each_module():
            colored = f"{m.CYAN}abc{m.RESET}"
            self.assertEqual(m.truncate_visible("abc", 3), "abc")
            self.assertEqual(m.truncate_visible("abc", 10), "abc")
            self.assertEqual(m.truncate_visible(colored, 3), colored)
            self.assertEqual(m.truncate_visible("", 5), "")

    def test_plain_text_is_cut_with_an_ellipsis(self):
        for m in self.each_module():
            self.assertEqual(m.truncate_visible("abcdefgh", 5), "abcd…")
            self.assertEqual(m.truncate_visible("abcdefgh", 1), "…")
            self.assertEqual(m.truncate_visible("abcdefgh", 0), "")
            self.assertEqual(m.truncate_visible("abcdefgh", -3), "")

    def test_ansi_codes_take_no_columns_and_end_with_reset(self):
        for m in self.each_module():
            text = f"{m.CYAN}{m.BOLD}abcdefgh{m.RESET} tail"
            cut = m.truncate_visible(text, 5)
            self.assertEqual(cut, f"{m.CYAN}{m.BOLD}abcd…{m.RESET}")
            self.assertEqual(m.visible_len(cut), 5)

    def test_color_that_starts_after_the_cut_is_dropped(self):
        for m in self.each_module():
            cut = m.truncate_visible(f"abcdefgh{m.CYAN}tail{m.RESET}", 5)
            self.assertEqual(cut, f"abcd…{m.RESET}")

    def test_wide_glyph_is_not_split(self):
        for m in self.each_module():
            self.assertEqual(m.visible_len("⚡"), 2)
            # "ab" + ellipsis uses 3 of 4 columns: the 2-column glyph does not fit in the last one.
            self.assertEqual(m.truncate_visible("ab⚡cdef", 4), "ab…")
            self.assertEqual(m.truncate_visible("ab⚡cdef", 5), "ab⚡…")

    def test_result_is_never_wider_than_the_limit(self):
        for m in self.each_module():
            text = f" {m.CYAN}⚡ host{m.RESET} " + "x⚡" * 60
            for width in range(0, 100):
                self.assertLessEqual(m.visible_len(m.truncate_visible(text, width)), width)


class BoxRowWidthTest(unittest.TestCase):
    def test_every_row_is_exactly_the_box_width(self):
        for m in MODULES:
            contents = [
                "",
                " short",
                " " + "a" * (m.BOX_INNER_WIDTH - 1),
                " " + "a" * m.BOX_INNER_WIDTH,
                f" {m.CYAN}{m.BOLD}⚡ " + "long-host-name." * 12 + m.RESET,
                " " + "⚡" * 60,
            ]
            for content in contents:
                with self.subTest(module=m.__name__, content=content[:20]):
                    self.assertEqual(m.visible_len(m.box_row(content)), m.BOX_INNER_WIDTH + 2)

    def test_long_row_ends_with_reset_before_the_border(self):
        m = cyber_tools
        row = m.box_row(f" {m.GRAY}" + "a" * 200)
        self.assertTrue(row.endswith(f"…{m.RESET}{m.MAGENTA}║{m.RESET}"))

    def test_header_with_a_long_subtitle_keeps_the_box_closed(self):
        m = cyber_tools
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            m.print_header("HTTP SECURITY HEADERS", "https://example.com/" + "a" * 120)
        lines = [line for line in out.getvalue().splitlines() if line]
        self.assertEqual({m.visible_len(line) for line in lines}, {m.BOX_INNER_WIDTH + 2})


if __name__ == "__main__":
    unittest.main()
