from textwrap import dedent


def _(document: str) -> str:
	"""Fix indentation from a multiline string to be a valid YAML document."""
	fixed = dedent(document).replace("\t", "  ")
	# Remove a single newline at the start and end, but no more so newline behaviour can actually be tested.
	fixed = fixed[1:-1]
	return fixed
