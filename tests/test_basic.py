"""Test basic app functionality."""
import os

from click.testing import CliRunner

from sphinx_emf.cli import run


def test_run_main():
    """Check whether main function runs through."""
    dir_this_file = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_this_file, "data", "prod", "config_sphinx_emf.py")
    runner = CliRunner()
    response = runner.invoke(run, [config_path])
    assert response.exit_code == 0
