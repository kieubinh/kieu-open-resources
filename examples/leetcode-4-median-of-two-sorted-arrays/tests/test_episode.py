import sys, unittest, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from episode import S

class TestEpisode(unittest.TestCase):
    def test_scene_ids(self): self.assertEqual(len(S),len({x.id for x in S}))
    def test_first_is_mission(self): self.assertEqual(S[0].mode,'mission')
    def test_silent_exact(self):
        pauses=[s for s in S if s.silent]
        self.assertEqual(len(pauses),1)
        self.assertEqual(pauses[0].script,'')
        self.assertEqual(pauses[0].min_seconds,10)
    def test_examples_before_hints_before_pause_before_code(self):
        modes=[x.mode for x in S]
        self.assertLess(modes.index('ex1'),modes.index('hints'))
        self.assertLess(modes.index('ex2'),modes.index('hints'))
        self.assertLess(modes.index('hints'),modes.index('think'))
        self.assertLess(modes.index('think'),modes.index('code1'))
    def test_stats_are_attributed(self):
        stats=next(s for s in S if s.mode=='stats')
        self.assertIn('46,4%',str(stats.lines))
        self.assertIn('Leetbot',stats.script)
        self.assertIn('04/09/2026',str(stats.lines))
    def test_timeline_frame_gate(self):
        rows=json.loads((ROOT/'src/timeline.json').read_text())
        self.assertEqual(len(rows),len(S))
        for a,b in zip(rows,rows[1:]):self.assertEqual(a['fromFrame']+a['frames'],b['fromFrame'])
        p=[x for x in rows if x['silent']]
        self.assertEqual(p[0]['frames'],300)
        self.assertFalse(p[0]['audio'])
        self.assertTrue(18*60<=sum(x['frames'] for x in rows)/30<=25*60)
    def test_three_related_challenges(self):
        lines=next(s.lines for s in S if s.mode=='practice')
        self.assertEqual(len(lines),3)
        for num in ['#35','#34','#378']:self.assertTrue(any(num in line for line in lines))

if __name__=='__main__':unittest.main()
