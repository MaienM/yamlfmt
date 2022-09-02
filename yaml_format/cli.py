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


def format(yaml: YAML, stream_in: TextIOBase, stream_out: TextIOBase):
	""" Read YAML from the input stream and write the formatted version to the output stream. """
	documents = yaml.load_all(stream_in)
	yaml.dump_all(documents, stream_out)


def get_parser() -> ArgumentParser:
	parser = ArgumentParser()
	parser.add_argument('-c', '--config', help='yamllint config file to use')
	parser.add_argument('-w', '--write', action='store_true', help='rewrite processed files in-place')
	parser.add_argument('paths', nargs='+', help='paths to process')
	return parser


def main():
	""" The main entrypoint. """
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
			format(yaml, stdin, stdout)
		else:
			if args.write:
				with StringIO() as stream_out:
					with open(path, 'r') as stream_in:
						format(yaml, stream_in, stream_out)
					with open(path, 'w') as f:
						f.write(stream_out.getvalue())
			else:
				with open(path, 'r') as stream_in:
					format(yaml, stream_in, stdout)
