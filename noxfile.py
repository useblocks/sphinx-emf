"""
Configuration file for nox.

May define a matrix build for dependency combinations.
"""

from nox_poetry import session


PYTHON_VERSIONS = ["3.7", "3.8", "3.9", "3.10"]
# DEP_VERSIONS = ["5.0.2"]


def run_tests(local_session) -> None:
    """Install the dependencies for the matrix build library versions and run the tests."""
    local_session.install(".")
    # session.run("pip", "install", f"lib=={lib_version}")
    # session.run("echo", "FINAL PACKAGE LIST", external=True)
    # session.run("pip", "freeze")
    local_session.run(
        "make", "test", external=True
    )  # runs 'poetry run pytest' which re-uses the active nox environment


@session(python=PYTHON_VERSIONS, reuse_venv=True)  # noqa: F841
# @nox.parametrize("lib_dependency", DEP_VERSIONS)  # add lib_dependency to the function params to enable matrix build
def tests(session):  # pylint: disable=redefined-outer-name
    """Run the nox matrix build test cases."""
    run_tests(session)
