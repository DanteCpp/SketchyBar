#!/usr/bin/env python3
"""Exercise native popup routing in a separate, temporary bar instance.

Run after `make clean && make arm64`. A transparent 1pt bar is briefly created
at the bottom of each display. No service, focus, pointer or config is changed.
"""
import json
import pathlib
import shutil
import subprocess
import tempfile
import time

root = pathlib.Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='machy-popup-test-') as directory:
    directory = pathlib.Path(directory)
    binary = directory / ('popup-test-' + str(time.time_ns()))
    shutil.copy2(root / 'bin/sketchybar', binary)
    config = directory / 'config'
    config.write_text('#!/bin/sh\n"' + str(binary) + '" --bar position=bottom height=1 color=0x00000000 shadow=off display=all '
                      '--default icon.drawing=off label.drawing=off '
                      '--add item test left --add item row popup.test '
                      '--set row width=20 background.height=10\n')
    config.chmod(0o700)
    with (directory / 'log').open('w') as log:
        daemon = subprocess.Popen([str(binary), '--config', str(config)], stdout=log, stderr=log)
        def call(*args):
            return subprocess.check_output([str(binary), *args], text=True, timeout=5, stderr=subprocess.DEVNULL)
        def query(name):
            return json.loads(call('--query', name))
        try:
            for _ in range(100):
                if daemon.poll() is not None:
                    raise RuntimeError((directory / 'log').read_text())
                try:
                    state = query('test')
                    if 'popup' in state:
                        break
                except (ValueError, subprocess.SubprocessError):
                    pass
                time.sleep(.05)
            else:
                raise AssertionError('Test bar did not start')
            assert state['popup']['display_id'] == 0
            displays = query('displays')
            for display in displays:
                adid = display['arrangement-id']
                for _ in range(3):
                    call('--set', 'test', 'popup.display=' + str(adid), 'popup.drawing=on')
                    assert query('test')['popup']['display_id'] == display['DirectDisplayID']
                    rects = query('row')['bounding_rects']
                    for other in displays:
                        x, y = rects['display-' + str(other['arrangement-id'])]['origin']
                        f = other['frame']
                        visible = f['x'] <= x < f['x'] + f['w'] and f['y'] <= y < f['y'] + f['h']
                        assert visible == (other == display), (adid, rects)
                    call('--set', 'test', 'popup.drawing=off')
            call('--set', 'test', 'popup.display=mouse', 'popup.drawing=on')
            did = query('test')['popup']['display_id']
            assert did in [d['DirectDisplayID'] for d in displays]
            try:
                call('--set', 'test', 'popup.display=invalid')
                raise AssertionError('Invalid display was accepted')
            except subprocess.CalledProcessError:
                pass
            assert query('test')['popup']['display_id'] == did
            call('--set', 'test', 'popup.display=active')
            assert query('test')['popup']['display_id'] == 0
            print('PASS: display routing, repeated open/close, mouse, active, invalid input;', len(displays), 'displays')
        finally:
            daemon.terminate()
            try:
                daemon.wait(timeout=5)
            except subprocess.TimeoutExpired:
                daemon.kill()
                daemon.wait()
