"""Structural tests for src/timeline.json (works for both the silent preview and the real-audio release timeline)."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_publish import CHAPTERS, chapters  # noqa: E402
from voicestudio import AUDIO_SLUG  # noqa: E402
from episode import PAUSE_ID, S  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TL = json.loads((ROOT / "src/timeline.json").read_text(encoding="utf-8"))
FPS = TL["fps"]


class TimelineTests(unittest.TestCase):
    def test_canvas_rate_and_scene_set(self):
        self.assertEqual(FPS, 30)
        self.assertEqual([s["id"] for s in TL["scenes"]], [s.id for s in S])

    def test_scenes_are_contiguous_and_total_matches(self):
        at = 0
        for s in TL["scenes"]:
            self.assertEqual(s["fromFrame"], at, s["id"])
            self.assertGreater(s["frames"], 0)
            at += s["frames"]
        self.assertEqual(at, TL["totalFrames"])

    def test_exactly_one_silent_pause_of_ten_seconds(self):
        silent = [s for s in TL["scenes"] if s["silent"]]
        self.assertEqual([s["id"] for s in silent], [PAUSE_ID])
        p = silent[0]
        self.assertEqual(p["frames"], 10 * FPS, "the thinking pause must be exactly 300 frames = 10.0 s")
        self.assertEqual(p["audio"], "")
        self.assertEqual(p["beats"], [], "no subtitle or narration during the pause")

    def test_beats_ordered_inside_scene_and_subtitles_do_not_overlap(self):
        for s in TL["scenes"]:
            prev_end = -1
            for k, b in enumerate(s["beats"]):
                self.assertGreaterEqual(b["startFrame"], prev_end, f"{s['id']} beat {k} overlaps previous subtitle")
                self.assertGreater(b["endFrame"], b["startFrame"], f"{s['id']} beat {k}")
                self.assertLessEqual(b["endFrame"], s["frames"], f"{s['id']} beat {k} runs past the scene")
                self.assertLessEqual(b["audioEndFrame"], s["frames"])
                prev_end = b["endFrame"]

    def test_scenes_adjacent_to_pause_have_no_trailing_or_leading_speech_overlap(self):
        ids = [s["id"] for s in TL["scenes"]]
        i = ids.index(PAUSE_ID)
        before, after = TL["scenes"][i - 1], TL["scenes"][i + 1]
        self.assertLessEqual(before["beats"][-1]["audioEndFrame"], before["frames"])
        self.assertGreaterEqual(after["beats"][0]["startFrame"], 0)

    def test_subtitle_text_equals_script_text(self):
        for s, row in zip(S, TL["scenes"]):
            self.assertEqual([b["text"] for b in row["beats"]], [b.text for b in s.beats], s.id)

    def test_audio_files_declared_for_every_spoken_scene(self):
        for row in TL["scenes"]:
            if row["silent"]:
                continue
            expected = "" if TL["preview"] else f"audio/{AUDIO_SLUG}/{row['id']}.wav"  # the preview timeline is silent by design
            self.assertEqual(row["audio"], expected)

    def test_youtube_chapters_valid(self):
        ch = chapters(TL)
        self.assertEqual(ch[0][0], "00:00")
        self.assertEqual(len(ch), len(CHAPTERS))
        self.assertGreaterEqual(len(ch), 3)


if __name__ == "__main__":
    unittest.main()
