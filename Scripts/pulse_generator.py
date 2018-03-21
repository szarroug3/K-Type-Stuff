import json
import argparse
from copy import copy
from random import randint


data = {
            "animations": {
                            "pulse_static": {
                                                "settings": "loops:1, framedelay:2, pfunc:interp,start"
                                            },
                            "pulse_changer": {
                                                "settings": "framedelay:5, loop, pfunc:interp,start"
                                             }
                          }
        }

def get_delta(start, end, color):
    if start[color] == end[color]:
        return 0
    return 1

def create_frames(start, end, deltas):
    for key in ['R', 'G', 'B']:
        if start[key] == end[key]:
            deltas[key] = 0
            continue
        if end[key] > start[key]:
            while deltas[key] > 0 and start[key] + deltas[key] > end[key]:
                deltas[key] -= 1
            start[key] += deltas[key]
            deltas[key + 'S'] = '+'
        else:
            while deltas[key] > 0 and start[key] - deltas[key] < end[key]:
                deltas[key] -= 1
            start[key] -= deltas[key]
            deltas[key + 'S'] = '-'
    return deltas, start

def equal_colors(color_a, color_b):
    for color in ['R', 'G', 'B']:
        if color_a[color] != color_b[color]:
            return False
    return  True

def switch_signs(data):
    for key in ['RS', 'GS', 'BS']:
        if data[key] == '+':
            data[key] = '-'
        else:
            data[key] = '+'
    return data

def pulse_writer(color_a, color_b, deltas):
    color_a.update({'RS': '+', 'GS': '+', 'BS': '+'})
    rgb_line = 'P[c:-10%]({RS}:{R},{GS}:{G},{BS}:{B}), P[c:110%]({RS}:{R},{GS}:{G},{BS}:{B})'
    frames = []
    backwards_frames = []
    static_frames = [rgb_line.format(**color_a)]
    while not equal_colors(color_a, color_b):
        deltas, color_a = create_frames(color_a, color_b, deltas)
        frames.append(rgb_line.format(**deltas))
        backwards_frames.insert(0, rgb_line.format(**switch_signs(deltas)))
    return static_frames, frames + backwards_frames

def pulse_writer_random(color_a, color_b, deltas):
    r_range = sorted([color_a['R'], color_b['R']])
    g_range = sorted([color_a['G'], color_b['G']])
    b_range = sorted([color_a['B'], color_b['B']])

    rgb_line = 'P[{K}]({RS}:{R},{GS}:{G},{BS}:{B})'

    frames = []
    backwards_frames = []
    static_frames = []

    for i in range(1, 120):
        start = {'R': randint(*r_range), 'G': randint(*g_range), 'B': randint(*b_range),
                 'RS': '+', 'GS': '+', 'BS': '+', 'K': i}
        deltas['K'] = i
        current = copy(start)
        current_deltas = copy(deltas)
        static_frames.append(rgb_line.format(**start))
        while not equal_colors(current, color_b):
            current_deltas, current = create_frames(current, color_b, current_deltas)
            frames.append(rgb_line.format(**current_deltas))
            backwards_frames.insert(0, rgb_line.format(**switch_signs(current_deltas)))
        frames += backwards_frames

        current = copy(start)
        current_deltas = copy(deltas)
        backwards_frames = []
        while not equal_colors(current, color_a):
            current_deltas, current = create_frames(current, color_a, current_deltas)
            frames.append(rgb_line.format(**current_deltas))
            backwards_frames.insert(0, rgb_line.format(**switch_signs(current_deltas)))
        frames += backwards_frames
    return static_frames, frames

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
              'B': get_delta(color_a, color_b, 'B') if not args.b_delta else abs(args.b_delta),
              'RS': '+', 'GS': '+', 'BS': '+'}

    if args.random:
        static, pulse = pulse_writer_random(color_a, color_b, deltas)
    else:
        static, pulse = pulse_writer(color_a, color_b, deltas)

    data['animations']['pulse_static']['frames'] = static
    data['animations']['pulse_changer']['frames'] = pulse
    with open('animation.json', 'w') as file:
        json.dump(data, file, indent=4)



# 236, 59, 154 -- pink
# 34, 160, 255 -- blue