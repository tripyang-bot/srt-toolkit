import unittest
from src import srt

SAMPLE = """1
00:00:01,000 --> 00:00:04,500
Hello there

2
00:00:05,000 --> 00:00:08,250
Second cue
"""


class SrtTest(unittest.TestCase):
    def test_parse(self):
        cues = srt.parse(SAMPLE)
        self.assertEqual(len(cues), 2)
        self.assertEqual(cues[0]["start_ms"], 1000)
        self.assertEqual(cues[1]["end_ms"], 8250)

    def test_shift_forward(self):
        cues = srt.shift(srt.parse(SAMPLE), 500)
        self.assertEqual(cues[0]["start_ms"], 1500)

    def test_negative_shift_beyond_start_is_rejected(self):
        # Shifting back by more than the first cue starts must not silently
        # clamp the timeline to zero; it should raise so the operator notices.
        with self.assertRaises(ValueError):
            srt.shift(srt.parse(SAMPLE), -2000)

    def test_roundtrip(self):
        self.assertEqual(srt.render(srt.parse(SAMPLE)), SAMPLE)


if __name__ == "__main__":
    unittest.main()
