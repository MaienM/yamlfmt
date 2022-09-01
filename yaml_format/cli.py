#!/usr/bin/env python

""" A simple YAML formatter. """

from sys import argv, stdin
from io import StringIO
from collections.abc import Iterable
from pathlib import Path

from ruyaml.main import YAML
from yamllint.config import YamlLintConfig
from yamllint.cli import find_files_recursively


def create_yaml() -> YAML:
	""" Create a YAML instance with the appropriate settings. """
	yaml = YAML()
	yaml.indent(mapping=2, sequence=4, offset=2)
	yaml.allow_duplicate_keys = True
	yaml.width = 120  # type: ignore
	yaml.explicit_start = True  # type: ignore
	return yaml


def format_source(source: str) -> str:
	""" Format the given YAML sourcecode. """
	yaml = create_yaml()
	with StringIO() as f:
		yaml.dump_all(yaml.load_all(source), f)
		return f.getvalue().strip() + '\n'


def format_file(fn: str) -> None:
	""" Format the given YAML file. """
	with open(fn, 'r', encoding='utf-8') as f:
		source = f.read()
	with open(fn, 'w', encoding='utf-8') as f:
		f.write(format_source(source))


def find_files(paths: Iterable[str], config: YamlLintConfig) -> Iterable[str]:
	"""
	Scan for files in the given paths.

	For each file path consider the path itself, for each directory path recursively scan for files.

	Respects the settings from the yamllint config.
	"""
	for fn in find_files_recursively(paths, config):
		if not config.is_file_ignored(fn):
			yield fn


def main():
	"""
	The main entrypoint.

	If only a single argument is passed ('-'), format stdin and output to stdout.
	If arguments are passed in these are used as paths to scan and format.
	If no arguments are provided scan for all files and format them.
	"""
	basedir = Path(__file__).parent.parent
	config = YamlLintConfig(file=basedir / '.yamllint.yaml')

	if argv[1:] == ['-']:
		print(format_source(stdin.read()))
		return

	for fn in find_files(argv[1:] if len(argv) > 1 else [basedir], config):
		format_file(fn)
