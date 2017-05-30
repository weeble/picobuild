import click
from collections import OrderedDict
import re
import os
import png


DIVIDER_REGEX = re.compile('^__([a-z]+)__$')
FRAGMENT_NAMES = ['header', 'lua', 'gfx', 'label', 'gff', 'map', 'sfx', 'music']


@click.group()
def main():
    pass


def read_p8(input):
    sections = OrderedDict()
    current = 'header'
    sections[current] = []
    for line in input:
        match = DIVIDER_REGEX.match(line)
        if match:
            current = match.group(1)
            sections[current] = []
            continue
        sections[current].append(line)
    return sections


def write_p8(output, sections):
    for fragment_name in FRAGMENT_NAMES:
        if fragment_name != 'header':
            output.write('__' + fragment_name + '__' + '\n')
        if fragment_name in sections:
            output.writelines(sections.get[fragment_name])


@main.command('update')
@click.argument('target', type=click.File('rt+'), required=True)
@click.option('--header', type=click.File('rt'))
@click.option('--lua', type=click.File('rt'))
@click.option('--gfx', type=click.File('rt'))
@click.option('--gff', type=click.File('rt'))
@click.option('--map', type=click.File('rt'))
@click.option('--sfx', type=click.File('rt'))
@click.option('--music', type=click.File('rt'))
@click.option('--output', type=click.File('wt'))
def update(target, header, lua, gfx, gff, map, sfx, music, output):
    p8 = read_p8(target)
    if header:
        p8['header'] = header.readlines()
    if lua:
        p8['lua'] = lua.readlines()
    if gfx:
        p8['gfx'] = gfx.readlines()
    if gff:
        p8['gff'] = gff.readlines()
    if map:
        p8['map'] = map.readlines()
    if sfx:
        p8['sfx'] = sfx.readlines()
    if music:
        p8['music'] = music.readlines()
    if output:
        target = output
    else:
        target.seek(0)
        target.truncate()
    write_p8(target, p8)


@main.command('extract')
@click.argument('input', type=click.File('rt'), required=True)
@click.option('--header', type=click.File('wt'))
@click.option('--lua', type=click.File('wt'))
@click.option('--gfx', type=click.File('wt'))
@click.option('--gff', type=click.File('wt'))
@click.option('--map', type=click.File('wt'))
@click.option('--sfx', type=click.File('wt'))
@click.option('--music', type=click.File('wt'))
def extract(input, header, lua, gfx, gff, map, sfx, music, all):
    p8 = read_p8(input)
    if header:
        header.writelines(p8['header'])
    if lua:
        lua.writelines(p8['lua'])
    if gfx:
        gfx.writelines(p8['gfx'])
    if gff:
        gff.writelines(p8['gff'])
    if map:
        map.writelines(p8['map'])
    if sfx:
        sfx.writelines(p8['sfx'])
    if music:
        music.writelines(p8['music'])

PICO8_PALETTE = [
    (0, 0, 0),        # black
    (29, 43, 83),     # dark-blue
    (126, 37, 83),    # dark-purple
    (0, 135, 81),     # dark-green
    (171, 82, 54),    # brown
    (95, 87, 79),     # dark-gray
    (194, 195, 199),  # light-gray
    (255, 241, 232),  # white
    (255, 0, 77),     # red
    (255, 163, 0),    # orange
    (255, 236, 39),   # yellow
    (0, 228, 54),     # green
    (41, 173, 255),   # blue
    (131, 118, 156),  # indigo
    (255, 119, 168),  # pink
    (255, 204, 170),  # peach
]


def parse_gfx_line(line):
    return [int(ch, 16) for ch in line.strip()]


def parse_map_line(line):
    return bytearray.fromhex(line.strip())


def convert_sprite_data_to_map_lines(slines):
    mlines=[]
    for i in range(0,64,2):
        left = slines[i]
        right = slines[i+1]
        combined = left + right
        joined = [l + 16*r for (l,r) in zip(combined[::2], combined[1::2])]
        mlines.append(joined)
    return mlines

def build_sprite_table(rgb_sprite_data):
    table={}
    for i in range(256):
        major_x = (i % 16) * 8
        major_y = (i // 16) * 8
        table[i] = [
            [
                rgb_sprite_data
                    [major_y + minor_y]
                    [major_x + minor_x]
                for minor_x in range(8)
            ]
            for minor_y in range(8)
        ]
    return table

def build_map_slice(indexes, sprite_table):
    lines=[]
    for y in range(8):
        lines.append([
            sprite_table[indexes[x//8]][y][x%8]
            for x in range(1024)
        ])
    return lines


@main.command('render-map')
@click.argument('input', type=click.File('rt', encoding='latin-1'), required=True)
@click.option('--output', type=click.Path(exists=False), required=True)
def render_map(input, output):
    '''
    Render the entire map as a 1024 * 512 RGB image.
    '''
    p8 = read_p8(input)
    indexed_sprite_data = [parse_gfx_line(line) for line in p8['gfx']]
    rgb_sprite_data = [[PICO8_PALETTE[i] for i in line] for line in indexed_sprite_data]
    shared_sprite_data = indexed_sprite_data[64:128]

    upper_map_data = [parse_map_line(line) for line in p8['map']]
    lower_map_data = convert_sprite_data_to_map_lines(shared_sprite_data)
    map_data = upper_map_data + lower_map_data

    stable = build_sprite_table(rgb_sprite_data)

    rgb_map_data = []
    for line in map_data:
        rgb_map_data.extend(build_map_slice(line, stable))

    with open(output, 'wb') as f:
        png.from_array(rgb_map_data, 'RGB').save(f)
        #png.from_array(rgb_sprite_data, 'RGB').save(f)


@main.command('extract-all')
@click.argument('input', type=click.File('rt'), required=True)
@click.option('--output', type=click.Path(exists=False))
def extract_all(input, output):
    if output is None:
        if hasattr(input, 'name'):
            output, ext = os.path.splitext(input.name)
        else:
            output = 'pico'
    p8 = read_p8(input)
    for fragment_name in FRAGMENT_NAMES:
        with click.open_file(output + '.' + fragment_name, 'wt') as f:
            f.writelines(p8[fragment_name])


if __name__ == '__main__':
    main()
