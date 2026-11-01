import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1] / "skills" / "kieu-ifelse-video"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SKILL / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_wav(path, seconds, tone=False):
    rate = 16000
    frame = (b"\x00\x20\x00\xe0" if tone else b"\x00\x00\x00\x00") * (rate * int(seconds + 1) // 2)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(frame[:int(seconds * rate) * 2])


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

    @unittest.skipUnless(importlib.util.find_spec("numpy"), "needs numpy from the studio venv")
    def test_asr_skip_words_are_not_missing(self):
        text = "Bạn bị bốn phẩy hai điểm Toán"
        with tempfile.TemporaryDirectory() as tmp, patch.object(self.voice, "hear", lambda *a: self.voice.toks("Bạn bị bốn hai điểm Toán")):
            take = Path(tmp) / "take.wav"
            write_wav(take, 2.0, tone=True)
            self.assertEqual(self.voice.score(None, take, text)["missing"], ["phẩy"])
            self.assertEqual(self.voice.score(None, take, text, ("phẩy",))["missing"], [])


class ScriptAuditTests(unittest.TestCase):
    def setUp(self):
        self.audit = load("audit_script")

    def test_episode_one_meets_the_hard_limits(self):
        text = (SKILL / "assets/starter-project/input/script.txt").read_text(encoding="utf-8")
        self.assertEqual(self.audit.hard_failures(self.audit.audit(text)), [])

    def test_episode_two_length_is_inside_the_hard_limit(self):
        self.assertEqual(self.audit.hard_failures(self.audit.audit("bạn " * 1616)), [])
        self.assertTrue(self.audit.hard_failures(self.audit.audit("bạn " * 1651)))

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
        self.assertIn("phẩy", data["asr_skip"])


@unittest.skipUnless(shutil.which("ffmpeg"), "needs ffmpeg")
class MakeShortTests(unittest.TestCase):
    def test_cuts_a_vertical_project_with_captions(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "projects/ep"
            for sub in ("scenes", "input", "timeline", "story"):
                (src / sub).mkdir(parents=True)
            (src / "scenes/cast.js").write_text("// cast", encoding="utf-8")
            write_wav(src / "input/voiceover.wav", 30.0)
            (src / "config.json").write_text(json.dumps({"title": "T", "aspect": "16:9", "captions": False, "script": "input/script.txt"}), encoding="utf-8")
            words = [{"word": w, "start": s, "end": s + 0.5} for w, s in (("trước", 5.0), ("một", 10.0), ("hai", 18.0), ("sau", 25.0))]
            (src / "timeline/words.json").write_text(json.dumps({"source": "x", "words": words}), encoding="utf-8")
            shots = [{"id": "a", "start": 0.0, "end": 12.0}, {"id": "b", "start": 12.0, "end": 22.0}, {"id": "c", "start": 22.0, "end": 30.0}]
            music = [{"mood": "calm", "start": 0.0, "end": 30.0}]
            (src / "story/shots.json").write_text(json.dumps({"shots": shots, "music": music}), encoding="utf-8")

            subprocess.run([sys.executable, str(SKILL / "scripts/make_short.py"), "projects/ep", "s1", "10", "20"], cwd=tmp, check=True, capture_output=True)

            dst = Path(tmp) / "projects/s1"
            cfg = json.loads((dst / "config.json").read_text(encoding="utf-8"))
            self.assertEqual((cfg["aspect"], cfg["captions"], cfg["duration"]), ("9:16", True, 11.2))
            self.assertNotIn("script", cfg)
            kept = json.loads((dst / "timeline/words.json").read_text(encoding="utf-8"))["words"]
            self.assertEqual([(w["word"], w["start"]) for w in kept], [("một", 0.0), ("hai", 8.0)])
            story = json.loads((dst / "story/shots.json").read_text(encoding="utf-8"))
            self.assertEqual([(s["id"], s["start"], s["end"]) for s in story["shots"]], [("a", 0, 2.0), ("b", 2.0, 11.2)])
            self.assertTrue((dst / "scenes/cast.js").exists())
            with wave.open(str(dst / "input/voiceover.wav")) as w:
                self.assertAlmostEqual(w.getnframes() / w.getframerate(), 11.2, places=1)


if __name__ == "__main__":
    unittest.main()
