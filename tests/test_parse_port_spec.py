"""Unit tests for the `--range` port specs parsed by `parse_port_spec()`."""

import contextlib
import io
import unittest

import cyber_tools


class ParsePortSpecTest(unittest.TestCase):
    def test_common_is_the_default_spec(self):
        self.assertEqual(cyber_tools.parse_port_spec("common"), sorted(cyber_tools.COMMON_PORTS))
        self.assertEqual(cyber_tools.parse_port_spec("COMMON"), sorted(cyber_tools.COMMON_PORTS))
        self.assertEqual(cyber_tools.parse_port_spec(""), sorted(cyber_tools.COMMON_PORTS))

    def test_explicit_ports_are_sorted_and_deduplicated(self):
        self.assertEqual(cyber_tools.parse_port_spec("443,22,80,80"), [22, 80, 443])
        self.assertEqual(cyber_tools.parse_port_spec(" 22 , 80 "), [22, 80])

    def test_ranges_are_inclusive(self):
        self.assertEqual(cyber_tools.parse_port_spec("1-3"), [1, 2, 3])
        self.assertEqual(cyber_tools.parse_port_spec("1-3,3-5"), [1, 2, 3, 4, 5])

    def test_reversed_range_is_read_as_the_same_range(self):
        self.assertEqual(cyber_tools.parse_port_spec("1024-1"), list(range(1, 1025)))
        self.assertEqual(cyber_tools.parse_port_spec("3-1"), [1, 2, 3])

    def test_ranges_are_clamped_to_the_port_space(self):
        self.assertEqual(cyber_tools.parse_port_spec("0-2"), [1, 2])
        self.assertEqual(cyber_tools.parse_port_spec("65534-65536"), [65534, 65535])

    def test_malformed_range_raises_a_friendly_error(self):
        for spec in ("web-80", "abc-def", "80-", "-80", "22-abc", "1--2"):
            with self.subTest(spec=spec):
                with self.assertRaises(ValueError) as ctx:
                    cyber_tools.parse_port_spec(spec)
                self.assertIn("Invalid port spec", str(ctx.exception))
                self.assertIn("1-1024", str(ctx.exception))

    def test_malformed_port_list_raises_a_friendly_error(self):
        for spec in ("22,,80", "22;80", "80.5", "http"):
            with self.subTest(spec=spec):
                with self.assertRaises(ValueError) as ctx:
                    cyber_tools.parse_port_spec(spec)
                self.assertIn("Invalid port spec", str(ctx.exception))

    def test_out_of_range_ports_are_reported_instead_of_dropped(self):
        for spec in ("0", "99999", "70000-80000"):
            with self.subTest(spec=spec):
                with self.assertRaises(ValueError) as ctx:
                    cyber_tools.parse_port_spec(spec)
                self.assertIn("outside 1-65535", str(ctx.exception))

    def test_error_message_names_the_offending_part_only(self):
        with self.assertRaises(ValueError) as ctx:
            cyber_tools.parse_port_spec("22,web-80,443")
        self.assertIn("'web-80'", str(ctx.exception))
        self.assertNotIn("'22,web-80,443'", str(ctx.exception))


class PortScannerSpecTest(unittest.TestCase):
    def test_port_scanner_prints_the_error_instead_of_a_traceback(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            cyber_tools.tool_port_scanner("127.0.0.1", "web-80")
        printed = out.getvalue()
        self.assertIn("Invalid port spec 'web-80'", printed)
        self.assertIn("✖", printed)


if __name__ == "__main__":
    unittest.main()
