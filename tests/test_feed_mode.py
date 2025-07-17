#test_feed_mode.py
#version 81
import asyncio
import sys
from types import SimpleNamespace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

sys.modules.setdefault('cv2', type('cv2', (), {}))
sys.modules.setdefault('torch', type('torch', (), {}))
sys.modules.setdefault('ultralytics', type('ultralytics', (), {'YOLO': object}))
sys.modules.setdefault('deep_sort_realtime', type('ds', (), {}))
sys.modules['deep_sort_realtime.deepsort_tracker'] = type('t', (), {'DeepSort': object})
sys.modules.setdefault('loguru', type('loguru', (), {'logger': type('l', (), {'info': lambda *a, **k: None})()}))
sys.modules.setdefault('PIL', type('PIL', (), {}))
sys.modules.setdefault('PIL.Image', type('PIL.Image', (), {}))
sys.modules.setdefault('imagehash', type('imagehash', (), {}))
sys.modules.setdefault('passlib', type('passlib', (), {}))
sys.modules.setdefault('passlib.hash', type('passlib.hash', (), {'pbkdf2_sha256': type('h', (), {'hash': lambda p: '', 'verify': lambda x, y: True})}))

from routers import dashboard


class DummyRequest:
    def __init__(self):
        self.session = {'user': {'role': 'viewer'}}


async def _run(mode):
    called = {}

    def fake_imencode(ext, frame):
        called['frame'] = frame
        class B:
            def tobytes(self):
                return b'img'
        return True, B()

    import cv2
    cv2.imencode = fake_imencode

    trackers = {
        1: SimpleNamespace(raw_frame=np.zeros((1, 1, 3), dtype='uint8'),
                           output_frame=np.ones((1, 1, 3), dtype='uint8'),
                           fps=1)
    }
    cams = [{'id': 1, 'name': 'Cam', 'dashboard_stream_mode': mode}]
    dashboard.init_context({'track_objects': ['person']}, trackers, cams, None)
    resp = await dashboard.live_feed(1, DummyRequest())
    gen = resp.body_iterator
    await gen.__anext__()
    return called['frame']


def test_feed_raw_mode():
    frame = asyncio.run(_run('raw'))
    assert (frame == 0).all()


def test_feed_debug_mode():
    frame = asyncio.run(_run('debug'))
    assert (frame == 1).all()

