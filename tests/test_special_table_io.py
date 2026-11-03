"""Separate processes simulate independent PCs; blocked OS read has a hard bound."""
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import special_table as m

class TableIOTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.folder=Path(self.temp.name)/'shared'
 def client(self,**kwargs):
  c=m.TableIO(self.folder,**kwargs);self.addCleanup(c.close);return c
 def test_three_independent_processes_merge_and_reuse_helpers(self):
  clients=[self.client() for _ in range(3)]
  ok,reply=clients[0].request([]);self.assertTrue(ok,reply);row=reply['state']['rows'][0]
  ops=[[{'kind':'cell','row':row['id'],'col':i,'base':row['cells'][i],'value':'PC'+str(i)}] for i in range(3)]
  with ThreadPoolExecutor(max_workers=3) as pool:
   replies=list(pool.map(lambda pair:pair[0].request(pair[1]),zip(clients,ops)))
  for ok,reply in replies:self.assertTrue(ok,reply);self.assertEqual(reply['conflicts'],[])
  process=clients[0].process;ok,reply=clients[0].request([])
  self.assertTrue(ok,reply);self.assertIs(clients[0].process,process)
  self.assertEqual(reply['state']['rows'][0]['cells'],['PC0','PC1','PC2'])
 @unittest.skipUnless(hasattr(os,'mkfifo'),'requires local FIFO')
 def test_blocked_share_read_times_out_then_reconnects(self):
  self.folder.mkdir();path=self.folder/'특수_돌출량.json';os.mkfifo(path)
  client=self.client(read_timeout=.4);start=time.monotonic();ok,message=client.request([])
  self.assertFalse(ok);self.assertIn('초과',message);self.assertLess(time.monotonic()-start,2)
  self.assertIsNone(client.process);path.unlink()
  ok,reply=client.request([]);self.assertTrue(ok,reply);self.assertEqual(len(reply['state']['rows']),26)

if __name__=='__main__':unittest.main()
