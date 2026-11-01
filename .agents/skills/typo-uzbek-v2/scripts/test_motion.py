import unittest,copy,json,os
from pathlib import Path
import numpy as np
from render import motion_array,validate,Event,PROFILE
from motion import spring_curve
ROOT=Path(__file__).resolve().parents[1]
class Contracts(unittest.TestCase):
 def test_exact_spring(self):
  for fps in (25,30,60):
   for key in ('y','scale','angle_x','angle_z'):
    frames=np.linspace(-5,70,170)
    np.testing.assert_allclose(motion_array(PROFILE['entry'],key,frames,fps),[spring_curve(PROFILE['entry'],key,f,fps) for f in frames],atol=1e-11)
 def test_real_speech_guards(self):
  cfg=json.loads((ROOT/'references/presenter-scene.json').read_text())
  source=os.environ.get('TYPO_V2_TEST_SOURCE')
  if not source:self.skipTest('Set TYPO_V2_TEST_SOURCE to the original presenter video')
  cfg['background']=source
  cfg['speech_evidence']=str(ROOT/'assets/studies/speech-evidence.json')
  validate(cfg)
  for key,val in [('text','ساختگی'),('start',.22)]:
   bad=copy.deepcopy(cfg);bad['events'][0]['words'][0][key]=val
   with self.assertRaises(ValueError):validate(bad)
  bad=copy.deepcopy(cfg);bad['events']*=2
  with self.assertRaises(ValueError):validate(bad)
 def test_overlay_boundaries(self):
  cfg=json.loads((ROOT/'references/presenter-scene.json').read_text());cfg['width']=540;cfg['height']=960
  e=Event(cfg['events'][0],cfg)
  self.assertIsNone(e.draw(e.start-.01));self.assertIsNone(e.draw(e.end+.01))
if __name__=='__main__':unittest.main()
