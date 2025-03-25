
.PHONY: pypi help test_pypi clean

help:
	@echo "This is a makefile to push to pypi."
	@echo "Use make pypi to push to pypi."

clean:
	\rm -rf dist *.egg-info

test_pypi:
	python3 -m twine upload --verbose --repository testpypi dist/*

pypi:   dist
	python3 -m twine upload --verbose dist/*

# Wheel is broken since it does not include html files
dist:
	python3 -m build --sdist


update:
	pip install --upgrade setuptools wheel twine build packaging
