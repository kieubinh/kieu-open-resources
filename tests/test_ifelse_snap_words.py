import importlib.util
import json
import shutil
import tempfile
import unittest
import wave
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills" / "kieu-ifelse-video"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SKILL / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def words(*rows):
    return [{"word": w, "start": s, "end": e} for w, s, e in rows]


class SnapWordsTests(unittest.TestCase):
    def setUp(self):
        self.snap = load("snap_words").snap

    def test_a_pause_inside_a_word_moves_its_start(self):
        W = words(("gọi", 1.0, 1.4), ("bạn", 1.4, 2.2))
        self.snap(W, [(1.6, 2.0)])
        self.assertEqual(W[1]["start"], 2.0)
        self.assertEqual(W[0]["end"], 1.6)

    def test_a_first_word_in_front_of_the_pause_moves_after_it(self):
        W = words(("đầu.", 5.0, 5.4), ("Năm", 5.4, 5.8), ("một", 5.8, 6.2), ("sáu", 6.2, 6.6))
        self.snap(W, [(5.45, 6.0)])
        self.assertEqual(W[1]["start"], 6.0)
        self.assertEqual(W[2]["start"], 6.15)  # pushed clear of the moved word's 0.15 s
        self.assertEqual(W[0]["end"], 5.45)

    def test_a_two_word_sentence_keeps_its_first_word_after_a_pause(self):
        # "Rồi... mất." with the EP03 start: the pause after "Rồi" must not take the word with it.
        W = words(("mất...", 159.4, 160.15), ("Rồi", 160.15, 160.25), ("mất.", 160.25, 160.8))
        self.snap(W, [(159.83, 160.15), (160.2, 160.6)])
        self.assertEqual(W[1]["start"], 160.15)
        self.assertEqual(W[2]["start"], 160.6)

    def test_a_two_word_sentence_stays_when_no_pause_ends_at_its_start(self):
        # EP03 timings. ASR heard "Hà Nội" in the 2.02-2.30 s sound and "Bạn ngồi" from 2.99 s.
        W = words(("sáu.", 1.8, 2.21), ("Hà", 2.21, 2.6), ("Nội.", 2.6, 2.99), ("Bạn", 2.99, 3.3), ("ngồi", 3.3, 3.6))
        self.snap(W, [(1.55, 2.02), (2.3, 2.994)])
        self.assertEqual(W[1]["start"], 2.21)
        self.assertEqual(W[3]["start"], 2.994)

    def test_a_first_word_already_on_a_pause_end_stays(self):
        W = words(("đó.", 9.0, 9.5), ("Bạn", 9.5, 9.6), ("ngồi", 9.6, 10.2), ("xuống.", 10.2, 10.6))
        self.snap(W, [(9.1, 9.5), (9.55, 9.9)])
        self.assertEqual(W[1]["start"], 9.5)

    def test_pauses_stay_paired_when_ffmpeg_reports_a_negative_start(self):
        log = "silence_start: -0.002\nsilence_end: 0.5 | silence_duration: 0.502\nsilence_start: 1.5\nsilence_end: 2 | silence_duration: 0.5\n"
        self.assertEqual(load("snap_words").parse_pauses(log), [(-0.002, 0.5), (1.5, 2.0)])

    def test_build_snaps_a_fresh_transcript_before_the_shots(self):
        steps = [(SKILL / "scripts/build_episode.sh").read_text(encoding="utf-8").index(x) for x in
                 ("tools/transcribe.py", "cp $P/timeline/words.json $P/timeline/words.raw.json", "snap_words.py $P", "story/build_shots.py")]
        self.assertEqual(steps, sorted(steps))

    @unittest.skipUnless(shutil.which("ffmpeg"), "needs ffmpeg")
    def test_rerun_starts_from_the_raw_words(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp); (p / "input").mkdir(); (p / "timeline").mkdir()
            rate = 16000; tone = b"\x00\x20\x00\xe0" * (rate // 2); quiet = b"\x00\x00" * rate
            with wave.open(str(p / "input/voiceover.wav"), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(tone + quiet + tone)
            raw = {"source": "test", "words": words(("gọi", 0.2, 0.9), ("bạn", 0.9, 2.5))}
            (p / "timeline/words.raw.json").write_text(json.dumps(raw), encoding="utf-8")
            snap_words = load("snap_words")
            snap_words.main(p); first = (p / "timeline/words.json").read_text(encoding="utf-8")
            snap_words.main(p)
            self.assertEqual((p / "timeline/words.json").read_text(encoding="utf-8"), first)
            self.assertEqual(json.loads((p / "timeline/words.raw.json").read_text(encoding="utf-8")), raw)
            self.assertAlmostEqual(json.loads(first)["words"][1]["start"], 2.0, delta=0.05)


if __name__ == "__main__":
    unittest.main()
