#!/usr/bin/env python

""" A simple YAML formatter. """

from argparse import ArgumentParser, FileType
from collections.abc import Iterable
from io import StringIO, TextIOBase
from sys import stdin, stdout

from ruyaml.main import YAML
from yamllint.config import YamlLintConfig
from yamllint.cli import find_files_recursively

from .config import load_config, create_yaml


def find_files(paths: Iterable[str], config: YamlLintConfig) -> Iterable[str]:
	"""
	Scan for files in the given paths.

	For each file path consider the path itself, for each directory path recursively scan for files.

	Respects the settings from the yamllint config.
	"""
	for fn in find_files_recursively(paths, config):
		if not config.is_file_ignored(fn):
			yield fn


def format_source(yaml: YAML, source: str) -> str:
	""" Format the given YAML sourcecode. """
	with StringIO() as f:
		yaml.dump_all(yaml.load_all(source), f)
		return f.getvalue().strip() + '\n'


def format_stream(yaml: YAML, file_in: TextIOBase, file_out: TextIOBase):
	source = file_in.read()
	formatted = format_source(yaml, source)
	file_out.write(formatted)


def get_parser() -> ArgumentParser:
	parser = ArgumentParser()
	parser.add_argument('-c', '--config', help='yamllint config file to use')
	parser.add_argument('-w', '--write', action='store_true', help='rewrite processed files in-place')
	parser.add_argument('paths', nargs='+', help='paths to process')
	return parser


def main():
	"""
	The main entrypoint.

	If only a single argument is passed ('-'), format stdin and output to stdout.
	If arguments are passed in these are used as paths to scan and format.
	If no arguments are provided scan for all files and format them.
	"""
	parser = get_parser()
	args = parser.parse_args()

	config = load_config(args.config)
	yaml = create_yaml(config)

	paths: List[str] = []
	for path in args.paths:
		if path == '-':
			paths.append('-')
		else:
			paths += find_files([path], config)

	for path in paths:
		if path == '-':
			format_stream(yaml, stdin, stdout)
		else:
			if args.write:
				with open(path, 'rw') as f:
					format_stream(yaml, f, f)
			else:
				with open(path, 'r') as f:
					format_stream(yaml, f, stdout)
