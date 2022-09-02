from os import environ
from pathlib import Path

from ruyaml.main import YAML
from yamllint.cli import find_files_recursively
from yamllint.config import YamlLintConfig


def load_config(path: Path | None) -> YamlLintConfig:
	""" Load the YamlLintConfig using the same rules as yamllint uses. """
	if path:
		return YamlLintConfig(file=path)

	for file in ['.yamllint', '.yamllint.yaml', '.yamllint.yml']:
		if Path(file).is_file():
			return YamlLintConfig(file=file)

	if 'YAMLLINT_CONFIG_FILE' in environ:
		return YamlLintConfig(file=environ['YAMLLINT_CONFIG_FILE'])

	user_config = Path(environ.get('XDG_CONFIG_HOME', '~')) / 'yamllint' / 'config'
	if user_config.is_file():
		return YamlLintConfig(file=user_config)

	return YamlLintConfig('extends: default')


def create_yaml(config: YamlLintConfig) -> YAML:
	""" Create a YAML instance with settings that match those from the YamlLintConfig. """
	yaml = YAML()

	# TODO: Actually setup based on the config.

	yaml.indent(mapping=2, sequence=4, offset=2)
	yaml.allow_duplicate_keys = True
	yaml.width = 120  # type: ignore
	yaml.explicit_start = True  # type: ignore

	return yaml
