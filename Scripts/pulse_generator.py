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
            "pulse": {"settings": "framedelay:2, loop, start"}
       }

def get_delta(start, end, delta_factor):
    deltas = {k: abs(end[k] - start[k]) for k in start.keys()}
    smallest = min(deltas.items(), key=lambda x: x[1])
    for k in deltas.keys():
        val = int(deltas[k]/smallest[1])
        if val <= 0:
            val = 1
        val *= delta_factor
        deltas[k] = val
    return deltas

def create_frames(start, end, color_deltas):
    frames = []
    reverse_frames = []
    current = copy(start)
    deltas = copy(color_deltas)
    while current != end:
        frames.append(copy(current))
        for key in ['R', 'G', 'B']:
            if current[key] == end[key]:
                deltas[key] = 0
            elif current[key] < end[key]:
                while deltas[key] > 0 and current[key] + deltas[key] > end[key]:
                    deltas[key] -= 1
                current[key] += deltas[key]
            else:
                while deltas[key] > 0 and current[key] - deltas[key] < end[key]:
                    deltas[key] -= 1
                current[key] -= deltas[key]
        reverse_frames.insert(0, copy(current))
    return frames + reverse_frames

def write_frames(frames, key=None):
    if key:
        pulse = 'P[{K}]({{R}},{{G}},{{B}})'.format(K=key)
    else:
        pulse = 'P[c:-10%]({R},{G},{B}), P[c:110%]({R},{G},{B})'
    return [pulse.format(**frame) for frame in frames]

def create_pulse(start, end, color_deltas, random=False):
    frames = create_frames(start, end, color_deltas)

    if not random:
        pulse = write_frames(frames)
        return pulse

    random_frames = {}
    for k in range(1, 120):
        start = randint(0, len(frames) - 1)
        pulse = write_frames(frames[start:] + frames[:start], key=k)
        random_frames[k] = pulse
    return [','.join(filter(None, frame)) for frame in zip_longest(*random_frames.values(), fillvalue='')]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a pulse rgb animation for the K-Type')
    parser.add_argument('color_a', type=str)
    parser.add_argument('color_b', type=str)
    parser.add_argument('--random', action='store_true', help='Start each key at a random color on the spectrum')
    parser.add_argument('-d', '--deltas', type=int, help='Delta values for RGB', nargs=3, metavar=('r_delta', 'g_delta', 'b_delta'))
    parser.add_argument('-f', '--delta-factor', type=int, help='Delta factor to multiply default deltas by', default=1)
    args = parser.parse_args()

    color_a = args.color_a.split(',')
    color_a = {'R': int(color_a[0].strip()), 'G': int(color_a[1].strip()), 'B': int(color_a[2].strip())}
    color_b = args.color_b.split(',')
    color_b = {'R': int(color_b[0].strip()), 'G': int(color_b[1].strip()), 'B': int(color_b[2].strip())}

    if args.deltas:
        deltas = dict(zip(['R', 'G', 'B'], args.deltas))
    else:
        deltas = get_delta(color_a, color_b, args.delta_factor)

    pulse = create_pulse(color_a, color_b, deltas, random=args.random)

    data['pulse']['frames'] = pulse
    filename = 'pulse_animation_{R}_{G}_{B}__{{R}}_{{G}}_{{B}}.json'.format(**color_a).format(**color_b)
    with open(os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Animations'), filename), 'w') as file:
        json.dump(data, file, indent=4)