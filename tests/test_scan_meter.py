"""تست‌های تقطیع‌یار: قواعد هجا، قاعده‌ی پایان مصراع، بحور و نمونه‌های تأییدشده."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import scan_meter as sm


class TestSyllable(unittest.TestCase):
    def test_short(self):
        for s in ("ma", "be", "to", "ke", "a", "o"):
            self.assertEqual(sm.parse_syllable(s), sm.U, s)

    def test_long(self):
        for s in ("fā", "lun", "dā", "ney", "now", "esh", "mī", "vī"):
            self.assertEqual(sm.parse_syllable(s), sm.L, s)

    def test_superlong(self):
        for s in ("kār", "dast", "eshgh", "yād", "ān"):
            self.assertEqual(sm.parse_syllable(s), sm.S, s)

    def test_invalid(self):
        for s in ("strt", "bārt", "kārā", "", "bc"):
            with self.assertRaises(sm.ScanError, msg=s):
                sm.parse_syllable(s)


class TestLineRules(unittest.TestCase):
    def test_final_always_long(self):
        _, pat = sm.scan_line("ma")
        self.assertEqual(pat, "-")
        _, pat = sm.scan_line("ma-fā")
        self.assertEqual(pat, "U-")

    def test_superlong_midline_expands(self):
        _, pat = sm.scan_line("kār-ma")
        self.assertEqual(pat, "-U-")

    def test_superlong_final_collapses(self):
        _, pat = sm.scan_line("ma-kār")
        self.assertEqual(pat, "U-")


class TestVerifiedLines(unittest.TestCase):
    RUMI_1 = "besh-no-vī-ney-chon-she-kā-yat-mī-ko-nad"
    RUMI_2 = "az-jo-dā-yī-hā-he-kā-yat-mī-ko-nad"
    BABA_1 = "be-sah-rā-ban-ga-ram-sah-rā-ta-vī-nam"
    BABA_2 = "be-dar-yā-ban-ga-ram-dar-yā-ta-vī-nam"

    def test_rumi_ramal(self):
        for line in (self.RUMI_1, self.RUMI_2):
            _, pat = sm.scan_line(line)
            self.assertEqual(pat, "-U---U---U-")
            self.assertIn("رمل مسدس محذوف", sm.match_meters(pat))

    def test_baba_hazaj(self):
        for line in (self.BABA_1, self.BABA_2):
            _, pat = sm.scan_line(line)
            self.assertEqual(pat, "U---U---U--")
            self.assertIn("هزج مسدس محذوف", sm.match_meters(pat))

    def test_broken_line_detected(self):
        broken = "besh-no-vī-ney-chon-ke-she-kā-yat-mī-ko-nad"
        _, pat = sm.scan_line(broken)
        self.assertNotEqual(pat, sm.METERS["رمل مسدس محذوف"][1])
        self.assertEqual(sm.match_meters(pat, "رمل مسدس محذوف"), [])

    def test_target_match_and_mismatch(self):
        _, pat = sm.scan_line(self.RUMI_1)
        self.assertEqual(sm.match_meters(pat, "رمل مسدس محذوف"), ["رمل مسدس محذوف"])
        self.assertEqual(sm.match_meters(pat, "هزج مسدس محذوف"), [])


class TestMeterTable(unittest.TestCase):
    def test_patterns_wellformed(self):
        for name, (arkan, pat) in sm.METERS.items():
            self.assertTrue(pat and set(pat) <= {"U", "-"}, name)
            self.assertTrue(arkan, name)

    def test_unknown_meter_raises(self):
        with self.assertRaises(sm.ScanError):
            sm.match_meters("U-", "بحر ناموجود")


if __name__ == "__main__":
    unittest.main()