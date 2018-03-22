import os
import json
import argparse
from copy import copy
from random import randint
try:
    from itertools import izip_longest
    zip_longest = izip_longest
except:
    from itertools import zip_longest


data = {
            "pulse_static": {"settings": "loops:1, framedelay:2, pfunc:interp,start"},
            "pulse_changer": {"settings": "framedelay:5, loop, pfunc:interp,start"}
       }

def get_delta(start, end, color):
    if start[color] == end[color]:
        return 0
    return 1

def create_frames(start, end, color_deltas):
    frames = []
    reverse_frames = []
    current = copy(start)
    deltas = copy(color_deltas)
    while current != end:
        frame = {'R': 0, 'G': 0, 'B': 0, 'RP': True, 'GP': True, 'BP': True}
        reverse = {'R': 0, 'G': 0, 'B': 0, 'RP': False, 'GP': False, 'BP': False}
        for key in ['R', 'G', 'B']:
            frame[key + 'C'] = current[key]
            if current[key] == end[key]:
                deltas[key] = 0
                frame[key + 'P'] = True
                reverse[key + 'P'] = False
            elif current[key] < end[key]:
                while deltas[key] > 0 and current[key] + deltas[key] > end[key]:
                    deltas[key] -= 1
                current[key] += deltas[key]
                frame[key + 'P'] = True
                reverse[key + 'P'] = False
            else:
                while deltas[key] > 0 and current[key] - deltas[key] < end[key]:
                    deltas[key] -= 1
                current[key] -= deltas[key]
                frame[key + 'P'] = False
                reverse[key + 'P'] = True
            frame[key] = deltas[key]
            reverse[key] = deltas[key]
            reverse[key + 'C'] = current[key]
        frames.append(frame)
        reverse_frames.insert(0, reverse)
    return frames + reverse_frames

def write_frames(frames, key=None):
    if key:
        static = 'P[{K}](+:{{RC}},+:{{GC}},+:{{BC}})'.format(K=key)
        pulse = 'P[{K}]({{RS}}:{{R}},{{GS}}:{{G}},{{BS}}:{{B}})'.format(K=key)
    else:
        static = 'P[c:-10%](+:{RC},+:{GC},+:{BC}), P[c:110%](+:{RC},+:{GC},+:{BC})'
        pulse = 'P[c:-10%]({RS}:{R},{GS}:{G},{BS}:{B}), P[c:110%]({RS}:{R},{GS}:{G},{BS}:{B})'
    return static.format(**frames[0]), [pulse.format(RS='+' if frame['RP'] else '-', GS='+' if frame['GP'] else '-', BS='+' if frame['BP'] else '-', **frame) for frame in frames]

def create_pulse(start, end, color_deltas, random=False):
    frames = create_frames(start, end, color_deltas)

    if not random:
        static, pulse = write_frames(frames)
        return [static], pulse

    random_frames = {}
    static_frames = []
    for k in range(1, 120):
        start = randint(0, len(frames) - 1)
        if k == 1:
            check(frames[start:] + frames[:start])
        static, pulse = write_frames(frames[start:] + frames[:start], key=k)
        static_frames.append(static)
        random_frames[k] = pulse
    return static_frames, [','.join(filter(None, frame)) for frame in zip_longest(*random_frames.values(), fillvalue='')]

def check(frames):
    curr = {'R': frames[0]['RC'], 'G': frames[0]['GC'], 'B': frames[0]['BC']}
    print(curr['R'], curr['G'], curr['B'])
    for f in frames:
        for k in curr.keys():
            if f[k + 'P']:
                curr[k] += f[k]
            else:
                curr[k] -= f[k]
        print(curr['R'], curr['G'], curr['B'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a pulse rgb animation for the K-Type')
    parser.add_argument('color_a', type=str)
    parser.add_argument('color_b', type=str)
    parser.add_argument('--random', action='store_true', help='Start each key at a random color on the spectrum')
    parser.add_argument('-r', '--r-delta', type=int, help='Delta for R value in RGB')
    parser.add_argument('-g', '--g-delta', type=int, help='Delta for G value in RGB')
    parser.add_argument('-b', '--b-delta', type=int, help='Delta for B value in RGB')
    args = parser.parse_args()

    color_a = args.color_a.split(',')
    color_a = {'R': int(color_a[0].strip()), 'G': int(color_a[1].strip()), 'B': int(color_a[2].strip())}
    color_b = args.color_b.split(',')
    color_b = {'R': int(color_b[0].strip()), 'G': int(color_b[1].strip()), 'B': int(color_b[2].strip())}

    deltas = {'R': get_delta(color_a, color_b, 'R') if not args.r_delta else abs(args.r_delta),
              'G': get_delta(color_a, color_b, 'G') if not args.g_delta else abs(args.g_delta),
              'B': get_delta(color_a, color_b, 'B') if not args.b_delta else abs(args.b_delta)}

    static, pulse = create_pulse(color_a, color_b, deltas, random=args.random)

    data['pulse_static']['frames'] = static
    data['pulse_changer']['frames'] = pulse
    filename = 'pulse_animation_{R}_{G}_{B}__{{R}}_{{G}}_{{B}}.json'.format(**color_a).format(**color_b)
    with open(os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Animations'), filename), 'w') as file:
        json.dump(data, file, indent=4)