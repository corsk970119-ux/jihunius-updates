"""apps/jihunius/app.pyw must always be the exact build of src/ and assets/."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_app import render  # noqa: E402


class BuildAppTests(unittest.TestCase):
    def test_committed_app_matches_sources(self):
        self.assertEqual((ROOT / 'apps/jihunius/app.pyw').read_bytes(), render(ROOT),
                         'run: python tools/build_app.py')

    def test_template_has_no_embedded_payloads(self):
        text = (ROOT / 'src/host/jihunius_main.py').read_text(encoding='utf-8')
        self.assertLess(max(len(line) for line in text.splitlines()), 1000)


if __name__ == '__main__':
    unittest.main()
