
.PHONY: pypi help

help:
	@echo "This is a makefile to push to pypi."
	@echo "Use make pypi to push to pypi."

pypi: README.md ox_profile/__init__.py
	python3 setup.py sdist
	twine upload --verbose -r pypi dist/*

ox_profile/__init__.py: README.rst
	echo '"""' > ox_profile/__init__.py
	cat README.md >> ox_profile/__init__.py
	echo '"""' >> ox_profile/__init__.py
