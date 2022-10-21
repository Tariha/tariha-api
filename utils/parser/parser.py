# -*- coding: utf-8 -*-
# Author: xxx
# Mail: xxx@xx
# Created Time: Wed Oct 05
from dataclasses import asdict
from pathlib import Path
from transcription.phonetic import unicode_to_phonetic 
from models import *
import json

def parse_xassida(file, depth):
    """Parse a single xassida file or xassida translation folder
       depth == 0 means that it's the arabic text
       else it's a translation text
    """
    xassida = file.absolute().parents[depth]
    author = xassida.parent
    tariha = author.parent
    print("Parsing %s "%(file.parent))
    xassida_data = {"name":xassida.stem}
    chapters = parse_file(file, depth)
    xassida_data["chapters"] = list(map(lambda c:Chapter(**c), chapters))
    result = asdict(Xassida(**xassida_data))
    file = xassida if depth == 0 else file.parent
    with open(file / f'{xassida.stem}.json', 'w') as jsonfile:
        json.dump(result, jsonfile, ensure_ascii=False)


def parse_file(file, depth):
    """Parse the file"""
    lang = False if depth == 0 else True
    lines = file.read_bytes().decode("utf-8").split("\n")
    return parse_chapter(lines, lang)


def parse_chapter(lines, lang):
    """Parse the chapters"""
    chapters = []
    chapter_number = 0
    verse_number = 0
    verse_text = ''

    for line in lines:
        if line.startswith("###"):
            if chapter_number > 0:
                chapter_data['verses'] = list(map(lambda v:Verse(**v), verses))
                chapters.append(chapter_data)

            verses = []
            chapter_number += 1
            chapter_data = {'name':line[3:].strip(), 'number':chapter_number}

        elif line.strip() == "##":
            if verse_number > 0:
                verse_data['text'] = verse_text.rstrip()
                phonetic_text = unicode_to_phonetic(verse_data['text']).split()
                if not lang:
                    verse_data['words'] = list(map(lambda x:Word(*x, phonetic_text[x[0]]), enumerate(verse_text.split())))
                verses.append(verse_data)

            verse_text = ''
            verse_number += 1
            verse_data = {'number':verse_number, 'key':f"{chapter_number}:{verse_number}"}

        else:
            verse_text += line.strip()+' '

    if verse_text:
        verse_data['text'] = verse_text.rstrip()
        phonetic_text = unicode_to_phonetic(verse_data['text']).split()
        if not lang:
            verse_data['words'] = list(map(lambda x:Word(*x, phonetic_text[x[0]]), enumerate(verse_text.split())))
        verses.append(verse_data)

        chapter_data['verses'] = list(map(lambda v:Verse(**v), verses))
        chapters.append(chapter_data)

    return chapters

if __name__ == '__main__':
    for file in Path("../../data/xassida").glob("**/*.txt"):
        if file.absolute().parents[4].stem == "xassida":
            depth = 1
        else:
            depth = 0
        parse_xassida(file, depth)
