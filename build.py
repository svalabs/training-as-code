#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script builds the presentation by filling the boilerplate with content
"""

import codecs
import configparser
import glob
import re
from itertools import zip_longest
from math import ceil

from jinja2 import Template


IGNORED_DOCS = [
    "CHANGELOG.md",
    "README.md",
    "README-remarkjs.md",
    "handout.md",
]
"""
IGNORED_DOCS: documents that will never be imported
"""

SLIDE_DIVIDER = '\n---\n'
POINTS_PER_AGENDA_SLIDE = 9
AGENDA_TEMPLATE = """
# Agenda {counter}
{points}

"""


def main():
    """
    Main function, starts the logic based on parameters.
    """
    config = read_config('settings.ini')
    slides = render_slides(read_slides(), config)

    template = read_template('template.html.j2')
    rendered_template = template.render(
        content=slides,
        ratio=config["layout"]["ratio"],
        **config["meta"],
    )

    write_file("presentation.html", rendered_template)


def read_config(filename):
    config = configparser.ConfigParser()
    config.read(filename, encoding='utf-8')
    return config


def read_template(filename):
    with open(filename) as file_:
        return Template(file_.read())


def read_slides():
    slides = []
    for file in sorted(glob.iglob("*.md")):
        if file not in IGNORED_DOCS:
            with open(file, 'r', encoding="utf-8") as slide_file:
                content = slide_file.read()

            slides.extend(
                [slide.strip() for slide in content.split(SLIDE_DIVIDER)]
            )

    if not slides:
        raise RuntimeError("No slides loaded. "
                           "Please add some slides or adjust IGNORED_DOCS.")

    return slides


def render_slides(slides, config):
    agenda = create_agenda(slides)
    print("On our agenda: {}".format(', '.join(agenda)))
    rendered_agenda = render_agenda(agenda)

    combined_slides = SLIDE_DIVIDER.join(slides)
    slide_template = Template(combined_slides)

    return slide_template.render(agenda=rendered_agenda, **config["meta"])


def create_agenda(slides):
    agenda = []
    for slide in slides[1:]:  # ignore title slide
        title = get_title(slide)
        if not title:
            continue

        if title not in agenda:
            agenda.append(title)

    return agenda


def get_title(slide):
    match = re.match(r'^(class: .*\n+){0,1}#\s+(?P<title>.*)$', slide, flags=re.MULTILINE)
    if match:
        title = match.group('title').strip()
        return title


def render_agenda(agenda):
    if not agenda:
        # Avoid having an empty slide.
        return ("Unable to detect agenda. "
                "Please add at least one first-level heading (`# Title`) "
                "or remove the `{{ agenda }}` tag from your slides.")

    slide_count = ceil(len(agenda) / POINTS_PER_AGENDA_SLIDE)

    filled_agenda = []
    for index, agenda_points in enumerate(chunks(agenda, POINTS_PER_AGENDA_SLIDE)):
        if slide_count < 2:
            count = ''
        else:
            count = '{index}/{count}'.format(index=index + 1,
                                             count=slide_count)

        topics = ['- %s' % t for t in agenda_points if t is not None]
        points = '\n'.join(topics)

        filled_agenda.append(AGENDA_TEMPLATE.format(counter=count,
                                                    points=points))

    return SLIDE_DIVIDER.join(filled_agenda)


def chunks(iterable, count):
    "Collect data into fixed-length chunks or blocks"
    # chunks('ABCDEFG', 3) --> ABC DEF Gxx"
    args = [iter(iterable)] * count
    return zip_longest(*args)


def write_file(filename, content):
    with codecs.open(filename, "w", "utf-8") as file_:
            file_.write(content)

if __name__ == "__main__":
    main()
