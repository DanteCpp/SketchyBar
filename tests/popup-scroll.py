#!/usr/bin/env python3
"""Verify scoped popup scrolling and per-row height overrides."""
import json
import pathlib
import shutil
import subprocess
import tempfile
import time

root = pathlib.Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='machy-popup-scroll-') as directory:
    directory = pathlib.Path(directory)
    binary = directory / ('popup-scroll-' + str(time.time_ns()))
    shutil.copy2(root / 'bin/sketchybar', binary)
    config = directory / 'config'
    commands = [
        f'"{binary}" --bar position=bottom height=1 color=0x00000000 shadow=off display=all',
        f'"{binary}" --default icon.drawing=off label.drawing=on',
        f'"{binary}" --add item test left',
        f'"{binary}" --add item head popup.test --set head label=HEAD width=80 cell_height=10',
        f'"{binary}" --add item list1 popup.test --set list1 label=ONE width=80 cell_height=20 scrollable=on',
        f'"{binary}" --add item list2 popup.test --set list2 label=TWO width=80 cell_height=20 scrollable=on',
        f'"{binary}" --add item list3 popup.test --set list3 label=THREE width=80 cell_height=20 scrollable=on',
        f'"{binary}" --add item list4 popup.test --set list4 label=FOUR width=80 cell_height=20 scrollable=on',
        f'"{binary}" --add item foot popup.test --set foot label=FOOT width=80 cell_height=10',
        f'"{binary}" --set test popup.max_height=64 popup.display=1 popup.drawing=on',
    ]
    config.write_text('#!/bin/sh\n' + '\n'.join(commands) + '\n')
    config.chmod(0o700)

    with (directory / 'log').open('w') as log:
        daemon = subprocess.Popen([str(binary), '--config', str(config)], stdout=log, stderr=log)

        def call(*args):
            return subprocess.check_output([str(binary), *args], text=True,
                                           timeout=5, stderr=subprocess.DEVNULL)

        def query(name):
            return json.loads(call('--query', name))

        try:
            for _ in range(100):
                if daemon.poll() is not None:
                    raise RuntimeError((directory / 'log').read_text())
                try:
                    state = query('test')
                    if state['popup']['scroll_max_offset'] == 2:
                        break
                except (KeyError, ValueError, subprocess.SubprocessError):
                    pass
                time.sleep(.05)
            else:
                raise AssertionError('Test popup did not become scrollable')

            popup = state['popup']
            assert popup['content_height'] == 100, popup
            assert popup['scroll_max_offset'] == 2, popup
            assert query('head')['geometry']['cell_height'] == 10
            assert query('list1')['geometry']['scrollable'] == 'on'

            head_before = query('head')['bounding_rects']['display-1']['origin']
            foot_before = query('foot')['bounding_rects']['display-1']['origin']
            one_before = query('list1')['bounding_rects']['display-1']['origin']
            call('--set', 'test', 'popup.scroll_offset=1')
            head_after = query('head')['bounding_rects']['display-1']['origin']
            foot_after = query('foot')['bounding_rects']['display-1']['origin']
            two_after = query('list2')['bounding_rects']['display-1']['origin']

            assert head_after == head_before, (head_before, head_after)
            assert foot_after == foot_before, (foot_before, foot_after)
            assert two_after == one_before, (one_before, two_after)
            print('PASS: fixed header/footer, scoped list scrolling, cell height')
        finally:
            daemon.terminate()
            try:
                daemon.wait(timeout=5)
            except subprocess.TimeoutExpired:
                daemon.kill()
                daemon.wait()
