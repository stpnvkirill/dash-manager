#!/usr/bin/env python

from __future__ import annotations

import logging
import os
import shutil
import sys
import textwrap

import click

from info import __version__

log = logging.getLogger(__name__)


class ColorFormatter(logging.Formatter):
    colors = {
        'CRITICAL': 'red',
        'ERROR': 'red',
        'WARNING': 'yellow',
        'DEBUG': 'blue',
    }

    text_wrapper = textwrap.TextWrapper(
        width=shutil.get_terminal_size(fallback=(0, 0)).columns,
        replace_whitespace=False,
        break_long_words=False,
        break_on_hyphens=False,
        initial_indent=' ' * 11,
        subsequent_indent=' ' * 11,
    )

    def format(self, record):
        message = super().format(record)
        prefix = f'{record.levelname:<8}-  '
        if record.levelname in self.colors:
            prefix = click.style(prefix, fg=self.colors[record.levelname])
        if self.text_wrapper.width:
            # Only wrap text if a terminal width was detected
            msg = '\n'.join(self.text_wrapper.fill(line) for line in message.splitlines())
            # Prepend prefix after wrapping so that color codes don't affect length
            return prefix + msg[11:]
        return prefix + message

class State:
    """Maintain logging level."""

    def __init__(self, log_name='mkdocs', level=logging.INFO):
        self.logger = logging.getLogger(log_name)
        # Don't restrict level on logger; use handler
        self.logger.setLevel(1)
        self.logger.propagate = False

        self.stream = logging.StreamHandler()
        self.stream.setFormatter(ColorFormatter())
        self.stream.setLevel(level)
        self.stream.name = 'MkDocsStreamHandler'
        self.logger.addHandler(self.stream)

    def __del__(self):
        self.logger.removeHandler(self.stream)

def add_options(*opts):
    def inner(f):
        for i in reversed(opts):
            f = i(f)
        return f

    return inner

def verbose_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        if value:
            state.stream.setLevel(logging.DEBUG)

    return click.option(
        '-v',
        '--verbose',
        is_flag=True,
        expose_value=False,
        help='Enable verbose output',
        callback=callback,
    )(f)

def quiet_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        if value:
            state.stream.setLevel(logging.ERROR)

    return click.option(
        '-q',
        '--quiet',
        is_flag=True,
        expose_value=False,
        help='Silence warnings',
        callback=callback,
    )(f)

def color_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        if value is False or (
            value is None
            and (
                not sys.stdout.isatty()
                or os.environ.get('NO_COLOR')
                or os.environ.get('TERM') == 'dumb'
            )
        ):
            state.stream.setFormatter(logging.Formatter('%(levelname)-8s-  %(message)s'))

    return click.option(
        '--color/--no-color',
        is_flag=True,
        default=None,
        expose_value=False,
        help="Force enable or disable color and wrapping for the output. Default is auto-detect.",
        callback=callback,
    )(f)

common_options = add_options(quiet_option, verbose_option)

PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"

PKG_DIR = os.path.dirname(os.path.abspath(__file__))


@click.group(name='dash-manager', context_settings=dict(help_option_names=['-h', '--help'], max_content_width=120))
@click.version_option(
    __version__,
    '-V',
    '--version',
    message=f'%(prog)s, version %(version)s from { PKG_DIR } (Python { PYTHON_VERSION })',
)
@common_options
@color_option
def cli():
    """
    DashManager - simple combining dash applications.
    """

@cli.command(name="new")
@click.argument("project_directory")
@common_options
def new_command(project_directory):
    """Create a new Dash project"""
    from commands import new

    new(project_directory)


if __name__ == '__main__':  # pragma: no cover
    cli()