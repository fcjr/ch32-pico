# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ch32-pico contributors
"""KiKit CLI with a live wx app and a checked native board loader on macOS.

Use absolute input/output paths. KiCad's project loader may change the process
working directory, making KiKit's later reload of a relative output fail.
Never pass a null board to the native zone filler.
"""
import wx
app=wx.App(False)
import pcbnew
original_load=pcbnew.LoadBoard


def checked_load(*args,**kwargs):
    board=original_load(*args,**kwargs)
    if board is None:raise RuntimeError(f'KiCad failed to load board: {args[0]}')
    return board


pcbnew.LoadBoard=checked_load
from kikit.ui import cli
cli()
