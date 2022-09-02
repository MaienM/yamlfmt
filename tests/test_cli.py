from io import StringIO
from pathlib import Path
from textwrap import dedent
from typing import List, Protocol
import sys

from pytest import fixture, CaptureFixture, MonkeyPatch

from yaml_format.cli import main


class CLIFixture(Protocol):
	@staticmethod
	def __call__(*args: List[str]):
		...


@fixture
def cli(monkeypatch: MonkeyPatch) -> CLIFixture:
	def helper(*args: List[str]) -> int:
		monkeypatch.setattr(sys, 'argv', [sys.argv[0]] + [str(a) for a in args])
		try:
			main()
		except SystemExit as e:
			return e.code
		return 0
	return helper


class PipeFixture():
	def __init__(self, stdin, stdout):
		self._stdin = stdin
		self._stdout = stdout

	def set_stdin(self, value: str):
		self._stdin.seek(0)
		self._stdin.write(value)
		self._stdin.seek(0)
	stdin = property(fset=set_stdin)
	del set_stdin

	@property
	def stdout(self) -> str:
		return self._stdout.getvalue()


@fixture
def pipe(monkeypatch: MonkeyPatch) -> PipeFixture:
	with StringIO() as stdin, StringIO() as stdout:
		monkeypatch.setattr('yaml_format.cli.stdin', stdin)
		monkeypatch.setattr('yaml_format.cli.stdout', stdout)

		yield PipeFixture(stdin, stdout)


def _(document: str) -> str:
	""" Fix indentation from a multiline string to be a valid YAML document. """
	fixed = dedent(document).replace('\t', '  ')
	# Remove a single newline at the start and end, but no more so newline behaviour can actually be tested.
	fixed = fixed[1:-1]
	return fixed


def test_stdin(pipe: PipeFixture, cli: CLIFixture):
	pipe.stdin = _('''
		test:   1
	''')

	assert cli('-') == 0
	assert pipe.stdout == _('''
		---
		test: 1

	''')


def test_single_file_stdout(tmp_path: Path, pipe: PipeFixture, cli: CLIFixture):
	path1 = tmp_path / 'file1.yaml'
	path1.write_text(_('''
		test:   1
	'''))

	assert cli(path1) == 0
	assert pipe.stdout == _('''
		---
		test: 1

	''')


def test_single_file_inplace(tmp_path: Path, pipe: PipeFixture, cli: CLIFixture):
	path1 = tmp_path / 'file1.yaml'
	path1.write_text(_('''
		test:   1
	'''))

	assert cli('-w', path1) == 0
	assert pipe.stdout == ''
	assert path1.read_text() == _('''
		---
		test: 1

	''')
