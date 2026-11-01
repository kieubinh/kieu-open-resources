import importlib.util
import json
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills" / "kieu-ifelse-video"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SKILL / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VoiceCheckTests(unittest.TestCase):
    def setUp(self):
        self.voice = load("voice")

    def test_reads_numbers_the_way_the_script_spells_them(self):
        self.assertEqual(self.voice.read_number(412), "bốn trăm mười hai")
        self.assertEqual(self.voice.read_number(250), "hai trăm năm mươi")
        self.assertEqual(self.voice.read_number(70000), "bảy mươi nghìn")
        self.assertEqual(self.voice.read_number(2006), "hai nghìn không trăm lẻ sáu")

    def test_digits_and_units_from_asr_match_spelled_words(self):
        self.assertEqual(self.voice.toks("2% năng lượng"), ["hai", "phần", "trăm", "năng", "lượng"])
        self.assertEqual(self.voice.toks("70.000 chữ số"), ["bảy", "mươi", "nghìn", "chữ", "số"])

    def test_accent_confusions_are_not_missing_words(self):
        want = self.voice.toks("Tối nào bà cũng hát ru")
        heard = self.voice.toks("Tối nào ba cũng hát du")
        self.assertEqual(self.voice.covered(want, heard), set(range(len(want))))

    def test_a_clipped_last_word_is_missing(self):
        want = self.voice.toks("Bạn không mất gì cả")
        heard = self.voice.toks("Bạn không mất gì")
        self.assertEqual(self.voice.covered(want, heard), {0, 1, 2, 3})

    def test_ledger_chunks_keep_every_word(self):
        text = (SKILL / "assets/starter-project/input/script.txt").read_text(encoding="utf-8")
        self.assertEqual(" ".join(self.voice.chunks(text)).split(), text.split())


class ScriptAuditTests(unittest.TestCase):
    def setUp(self):
        self.audit = load("audit_script")

    def test_episode_one_meets_the_hard_limits(self):
        text = (SKILL / "assets/starter-project/input/script.txt").read_text(encoding="utf-8")
        self.assertEqual(self.audit.hard_failures(self.audit.audit(text)), [])

    def test_title_rules(self):
        self.assertEqual(self.audit.title_failures("Nếu Trí Nhớ Của Bạn Mạnh Gấp 100 Lần?"), [])
        self.assertTrue(self.audit.title_failures("Trí nhớ siêu phàm"))


class KitPatchTests(unittest.TestCase):
    def setUp(self):
        self.patch = load("patch_kit")

    def test_swapped_brows_are_fixed_once(self):
        bad = "if (ex.brows === 'worried') { brow(eyeX[0], -r * 0.06); brow(eyeX[1], r * 0.06); }"
        good = "if (ex.brows === 'worried') { brow(eyeX[0], r * 0.06); brow(eyeX[1], -r * 0.06); }"
        self.assertEqual(self.patch.fix_rig(bad), good)
        self.assertEqual(self.patch.fix_rig(good), good)


class MetadataTests(unittest.TestCase):
    def test_srt_and_chapters(self):
        meta = load("make_meta")
        words = [{"word": "Bạn.", "start": 0.5, "end": 1.0}, {"word": "Nhớ.", "start": 62.0, "end": 62.5}]
        self.assertIn("00:01:02,000 --> 00:01:02,", meta.srt(words))
        shots = {"a": {"start": 0.3}, "b": {"start": 62.0}}
        self.assertEqual(meta.chapters(shots, [["a", "Mở"], ["b", "Hai"]]), "0:00 Mở\n1:02 Hai")

    def test_example_settings_are_valid_json(self):
        data = json.loads((SKILL / "assets/episode.example.json").read_text(encoding="utf-8"))
        self.assertEqual(data["voice"]["speed"], 1.1)


if __name__ == "__main__":
    unittest.main()
