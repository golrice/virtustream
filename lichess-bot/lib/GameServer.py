"""Provides communication with the engine."""
from __future__ import annotations
import os
import chess.engine
import chess.polyglot
import chess.syzygy
import chess.gaviota
import chess
from chess.engine import PlayResult
import subprocess
import logging
import copy
import datetime
import time
import random
import math
import select
import socket
import contextlib
# from collections import Counter
# from collections.abc import Callable

# from extra_game_handlers import game_specific_options
# from operator import itemgetter
# from typing import Any, Optional, Union, Literal, cast
# from types import TracebackType
move = "e1e2"
best_move = PlayResult(move=chess.Move.from_uci(move), ponder=True)
move1 = chess.Move.from_uci("a1a2")
best_move.move = move1
print(type(best_move.move),str(best_move.move))
# move = ""
# if move:
#     print("yes")
# else:
#     print("null")