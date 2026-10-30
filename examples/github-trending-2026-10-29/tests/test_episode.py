import json, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from episode import S, EPISODES  # noqa: E402
import config  # noqa: E402

BEATS = ['intro', 'growth', 'why', 'problem', 'how', 'usage', 'value', 'ideas', 'outro']
MANIFEST = json.loads((ROOT / 'docs/SOURCE_MANIFEST.json').read_text())


class EpisodeStructure(unittest.TestCase):
    def test_skill_audit_passes(self):
        audit = ROOT.parents[1] / 'skills/kieu-github-video/scripts/audit_episode.py'
        r = subprocess.run([sys.executable, str(audit), '--episode', str(ROOT / 'scripts/episode.py')], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_one_repo_per_video_nine_beats_and_a_caveat(self):
        self.assertEqual(sorted(EPISODES), ['gr01', 'gr02', 'gr03'])
        seen = set()
        for name, scenes in EPISODES.items():
            repos = {s.repo for s in scenes}
            self.assertEqual(len(repos), 1, name)
            self.assertFalse(repos & seen, 'a repo must appear in only one video')
            seen |= repos
            self.assertEqual([s.beat for s in scenes], BEATS)
            value = next(s for s in scenes if s.beat == 'value')
            self.assertGreater(len(value.lines), value.data['caveat_from'])

    def test_default_speed_is_normal(self):
        self.assertEqual(config.VIDEO_SPEED, 1.0)


class FactsMatchManifest(unittest.TestCase):
    def test_numbers_on_screen_equal_manifest(self):
        by_repo = {r['full_name']: r for r in MANIFEST['repos']}
        fmt = lambda n: f'{n:,}'.replace(',', '.')
        for scenes in EPISODES.values():
            for s in scenes:
                m = by_repo[s.repo]
                if s.beat == 'intro':
                    chips = {label: value for _, label, value in s.data['chips']}
                    self.assertEqual(chips['Fork'], fmt(m['forks']))
                    self.assertEqual(chips['Giấy phép'], m['license'])
                if s.beat == 'growth':
                    self.assertEqual((s.data['total'], s.data['month'], s.data['week'], s.data['today']),
                                     (m['stars_total'], m['stars_month'], m['stars_week'], m.get('stars_today')))

    def test_chart_points_and_rates_match_manifest(self):
        by_repo = {r['full_name']: r for r in MANIFEST['repos']}
        for scenes in EPISODES.values():
            g = next(s for s in scenes if s.beat == 'growth'); m = by_repo[g.repo]; d = m['derived']
            self.assertEqual(g.data['pts'][0][1], d['stars_30_days_ago']); self.assertEqual(g.data['pts'][-1][1], m['stars_total'])
            if m.get('stars_week'):
                self.assertEqual(g.data['pts'][1][1], d['stars_7_days_ago'])
                self.assertEqual(g.data['segs'], [d['avg_per_day_first_23_days'], d['avg_per_day_last_7_days']])
                self.assertIn(str(d['seconds_per_star_last_7_days']), g.data['tick'])
            else:
                self.assertEqual(len(g.data['pts']), 2)  # no 7-day figure listed: do not invent a middle point
                self.assertIsNone(g.data['segs'])

    def test_derived_numbers(self):
        for m in MANIFEST['repos']:
            self.assertEqual(m['derived']['stars_30_days_ago'], m['stars_total'] - m['stars_month'])
            self.assertEqual(m['derived']['avg_stars_per_day_30d'], round(m['stars_month'] / 30))

    def test_every_repo_has_licence_sources_and_caveats(self):
        for m in MANIFEST['repos']:
            self.assertTrue(m['license'] and m['sources'] and m['caveats'])


class Gates(unittest.TestCase):
    def test_no_digits_longer_than_four_in_narration(self):
        import re
        for scenes in EPISODES.values():
            for s in scenes:
                self.assertIsNone(re.search(r'\d{5,}', s.script), s.id)

    def test_voice_adapter_is_local_only(self):
        text = (ROOT / 'scripts/voicestudio.py').read_text()
        self.assertIn("http://127.0.0.1:", text)
        self.assertIn('no fallback', text)

    def test_avatar_geometry_matches_owner_default(self):
        tsx = (ROOT / 'src/SpeakingAvatar.tsx').read_text()
        self.assertIn('D = 220, RIGHT = 64, BOTTOM = 64, BORDER = 4', tsx)
        self.assertIn('#72dce0', tsx)

    def test_lipsync_mouth_is_wired_and_matches_timeline(self):
        tsx = (ROOT / 'src/SpeakingAvatar.tsx').read_text()
        for needle in ('const Mouth', 'mouthO', 'kieu-avatar-nomouth.png', 'Silence closes the lips'):
            self.assertIn(needle, tsx)
        anchor = json.loads((ROOT / 'src/avatar.mouth.json').read_text())
        self.assertEqual(set(anchor), {'cx', 'cy', 'width', 'tilt'})
        if not ((ROOT / 'src/mouth.json').exists() and (ROOT / 'src/timeline.json').exists()):
            self.skipTest('generated tracks missing: run npm run timeline:preview')
        mouth = json.loads((ROOT / 'src/mouth.json').read_text()); tl = json.loads((ROOT / 'src/timeline.json').read_text())
        if set(mouth) != {r['id'] for r in tl}:
            self.skipTest('mouth.json belongs to another episode: rebuild with npm run timeline:preview')
        for r in tl:
            self.assertEqual(len(mouth[r['id']]['o']), r['frames']); self.assertEqual(len(mouth[r['id']]['s']), r['frames'])
            self.assertTrue(all(0 <= v <= 1 for v in mouth[r['id']]['o']))

    def test_subtitles_clear_of_avatar(self):
        tsx = (ROOT / 'src/GitHubRadar.tsx').read_text()
        self.assertIn('right: 330', tsx)

    def test_remotion_folder_name_is_valid(self):
        import re
        name = re.search(r'<Folder name="([^"]+)"', (ROOT / 'src/root.tsx').read_text()).group(1)
        self.assertRegex(name, r'^[A-Za-z0-9-]+$')


if __name__ == '__main__':
    unittest.main()
