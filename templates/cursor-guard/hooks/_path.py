"""Bootstrap: 将 hooks/_lib 加入 sys.path（供入口脚本 import hook_io 前加载）。"""
from __future__ import annotations

import sys
from pathlib import Path

_LIB = Path(__file__).resolve().parent / "_lib"
if str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))
