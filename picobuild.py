import click
from collections import OrderedDict
import re
import os

DIVIDER_REGEX = re.compile('^__([a-z]+)__$')
FRAGMENT_NAMES = ['header', 'lua', 'gfx', 'gff', 'map', 'sfx', 'music']


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
        output.writelines(sections[fragment_name])


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
