"""Structure, narration and Vietnamese-text tests for EP03. Run with the other tests:
python3 -m unittest discover -s scripts -p '*test.py' -v"""
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import episode  # noqa: E402
from oracles import regex_oracle  # noqa: E402
from vi_text import vi_decimal, vi_int, vn_group  # noqa: E402

ROOT = HERE.parent
SKILL = ROOT.parent.parent / "skills/kieu-leetcode-video/scripts"


class VietnameseNumbers(unittest.TestCase):
    def test_known_readings(self):
        cases = {0: "không", 5: "năm", 10: "mười", 14: "mười bốn", 15: "mười lăm", 21: "hai mươi mốt", 25: "hai mươi lăm",
                 100: "một trăm", 105: "một trăm lẻ năm", 2000: "hai nghìn", 2026: "hai nghìn không trăm hai mươi sáu",
                 20000: "hai mươi nghìn", 203078: "hai trăm lẻ ba nghìn không trăm bảy mươi tám",
                 967654: "chín trăm sáu mươi bảy nghìn sáu trăm năm mươi bốn",
                 173355: "một trăm bảy mươi ba nghìn ba trăm năm mươi lăm", 4000000: "bốn triệu",
                 1002001: "một triệu không trăm lẻ hai nghìn không trăm lẻ một"}
        for n, text in cases.items():
            self.assertEqual(vi_int(n), text, n)

    def test_decimal_and_grouping(self):
        self.assertEqual(vi_decimal("33,1"), "ba mươi ba phẩy một")
        self.assertEqual(vi_decimal("0,592"), "không phẩy năm chín hai")
        self.assertEqual(vn_group(967654), "967.654")


class EpisodeStructure(unittest.TestCase):
    def test_ids_unique_and_one_silent_pause_of_ten_seconds(self):
        ids = [s.id for s in episode.S]
        self.assertEqual(len(ids), len(set(ids)))
        silent = [s for s in episode.S if s.silent]
        self.assertEqual([s.id for s in silent], [episode.PAUSE_ID])
        self.assertEqual(silent[0].min_seconds, 10.0)
        self.assertEqual(silent[0].beats, ())  # no narration, no subtitles during the pause

    def test_pedagogical_order(self):
        modes = [s.mode for s in episode.S]
        order = ["mission", "problem", "constraints", "stats", "ex1", "ex2", "ex3", "hints", "think", "rules", "tree",
                 "blowup", "greedy_fail", "dp", "insight", "greedy", "trace", "pseudocode", "code1", "code2", "verify",
                 "complexity", "lessons", "practice", "outro"]
        positions = [modes.index(m) for m in order]
        self.assertEqual(positions, sorted(positions))

    def test_two_to_three_hints_before_the_pause(self):
        hints = next(s for s in episode.S if s.mode == "hints")
        self.assertEqual(len([line for line in hints.lines if line.startswith(("GỢI Ý", "HINT"))]), 3)
        self.assertLess(episode.S.index(hints), [s.id for s in episode.S].index(episode.PAUSE_ID))

    def test_three_practice_problems_with_verified_difficulty(self):
        self.assertEqual([(p["n"], p["difficulty"]) for p in episode.PRACTICE], [(392, "Easy"), (72, "Medium"), (10, "Hard")])
        practice = next(s for s in episode.S if s.mode == "practice")
        self.assertEqual(len(practice.lines), 3)

    def test_official_numbers_are_exactly_those_verified_on_28_oct_2026(self):
        self.assertEqual(episode.STATS, {"date": "2026-10-28", "accepted": 967654, "total_display": "2.9M", "acceptance": "33.1%"})
        stats = next(s for s in episode.S if s.mode == "stats")
        en = episode.LANG == "en"
        self.assertIn("967,654" if en else "967.654", stats.script)
        self.assertIn("33.1%" if en else "33,1%", stats.script)

    def test_pause_neighbours_have_no_padding(self):
        from voicestudio import scene_layout
        index = [s.id for s in episode.S].index(episode.PAUSE_ID)
        self.assertEqual(scene_layout(index - 1)[1], 0.0)
        self.assertEqual(scene_layout(index + 1)[0], 0.0)

    def test_code_cues_stay_inside_the_displayed_source(self):
        from build_trace import source_block
        lines, _ = source_block()
        for s in episode.S:
            if s.mode == "code1":
                for beat in s.beats:
                    lo, hi = beat.cue
                    self.assertTrue(0 <= lo <= hi < len(lines), (s.id, beat.cue))

    def test_code2_cues_are_increasing_trace_steps(self):
        scene = next(s for s in episode.S if s.mode == "code2")
        cues = [b.cue for b in scene.beats]
        self.assertEqual(cues, sorted(cues))
        self.assertEqual(len(set(cues)), len(cues))


class NarrationText(unittest.TestCase):
    FORBIDDEN = re.compile(r"[0-9*=#%()\[\]_<>/\\|{}+×≤≥≠→·]|(^|[\s(])\?")

    @unittest.skipIf(episode.LANG == "en", "Vietnamese TTS rule; the English voice reads digits")
    def test_spoken_text_has_no_digits_or_symbols(self):
        for scene, k, beat in episode.all_beats():
            self.assertIsNone(self.FORBIDDEN.search(beat.spoken), (scene.id, k + 1, beat.spoken))

    @unittest.skipIf(episode.LANG == "en", "Vietnamese pronunciation rule")
    def test_brand_is_spoken_in_vietnamese(self):
        for scene, k, beat in episode.all_beats():
            self.assertNotIn("Kieu", beat.spoken, (scene.id, k + 1))
            self.assertNotIn("kieu.app", beat.spoken)

    def test_subtitles_are_short_enough(self):
        for scene, k, beat in episode.all_beats():
            self.assertLessEqual(len(beat.text), 135, (scene.id, k + 1, len(beat.text)))
            self.assertGreaterEqual(len(beat.text), 12)

    def test_each_scene_has_narration_except_the_pause(self):
        for scene in episode.S:
            if not scene.silent:
                self.assertGreaterEqual(len(scene.beats), 2, scene.id)

    def test_demo_pattern_on_the_problem_slide_is_valid(self):
        # The animation on the problem slide aligns "abcde" with "a?*e": a, ?=b, *=cd, e.
        self.assertTrue(regex_oracle("abcde", "a?*e"))


class SkillAudit(unittest.TestCase):
    def test_reusable_skill_audit_passes(self):
        sys.path.insert(0, str(SKILL))
        import audit_episode
        self.assertEqual(audit_episode.audit(HERE / "episode.py"), 0)


if __name__ == "__main__":
    unittest.main()
