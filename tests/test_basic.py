"""Test basic app functionality."""
import filecmp
import logging
import os
import subprocess
import sys
import textwrap

from click.testing import CliRunner

from sphinx_emf.cli import run


DIR_THIS_FILE = os.path.dirname(os.path.realpath(__file__))


def test_basic_cli(tmp_path, caplog):
    """Check the CLI for exit code 0."""
    caplog.set_level(logging.DEBUG)

    conf_file = tmp_path / "config.py"

    data_path = os.path.abspath(os.path.join(DIR_THIS_FILE, "data", "base"))
    ecore_path = os.path.join(data_path, "base_test.ecore")
    rst_out_path = str(tmp_path / "out.rst")
    config_common = gen_common_conf(ecore_path)
    config_cli = gen_cli_conf(data_path, rst_out_path)
    config = config_common + config_cli
    conf_file.write_text(config)
    runner = CliRunner()
    response = runner.invoke(run, [str(conf_file)])
    assert response.exit_code == 0


def test_basic_roundtrip(tmp_path, caplog):
    """Check whether main function runs through."""
    caplog.set_level(logging.DEBUG)

    conf_file_cli = tmp_path / "config_cli.py"

    data_path = os.path.abspath(os.path.join(DIR_THIS_FILE, "data", "base"))
    ecore_path = os.path.join(data_path, "base_test.ecore")
    rst_out_path = str(tmp_path / "index.rst")
    config_common = gen_common_conf(ecore_path)
    config_cli = gen_cli_conf(data_path, rst_out_path)
    all_config = config_common + config_cli
    conf_file_cli.write_text(all_config)
    runner = CliRunner()
    response = runner.invoke(run, [str(conf_file_cli)])
    assert response.exit_code == 0

    # run the sphinx builder now
    config_builder = gen_builder_conf()
    config_needs = gen_sphinx_needs_conf()
    all_config = config_needs + config_common + config_builder
    conf_file_builder = tmp_path / "conf.py"
    conf_file_builder.write_text(all_config)
    # get current python interpreter so run sphinx-build from it

    dir_bin = "Scripts" if sys.platform == "win32" else "bin"
    path_sphinx_build = os.path.join(sys.prefix, dir_bin, "sphinx-build")
    completed_process = subprocess.run(
        [path_sphinx_build, "-c", str(tmp_path), "-b", "emf", str(tmp_path), str(tmp_path / "_build" / "emf")],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert completed_process.returncode == 0
    assert len(completed_process.stderr) == 0  # nothing expected in stderr

    # compare input XMI and output XMI for equality, also XML formatting should not differ
    path_in = os.path.join(data_path, "base_test.xmi")
    path_out = str(tmp_path / "_build" / "emf" / "m1_model_out.xmi")
    compare_result = filecmp.cmp(path_in, path_out, shallow=False)
    assert compare_result  # files must be identical


def gen_cli_conf(data_path, rst_out_path):
    """Generate the sphinx-emf config part for CLI."""
    xmi_path = os.path.join(data_path, "base_test.xmi")
    templates_path = os.path.join(data_path, "templates")
    return textwrap.dedent(
        f"""\
        emf_path_m1_model = r"{xmi_path}"
        emf_rst_indent = 3
        emf_allowed_classes = []
        emf_denied_classes = []
        emf_allowed_values = {{}}
        emf_denied_values = {{}}
        emf_sort_field = "_internal_id"
        emf_templates_dir = r"{templates_path}"
        emf_show_nested_need_title = True
        emf_rst_output_configs = [
            {{
                "path": r"{rst_out_path}",
                "emf_types": ["Root"],
            }},
        ]
        """
    )


def gen_builder_conf():
    """Generate the sphinx-emf config part for the Sphinx builder."""
    return textwrap.dedent(
        """\
        emf_model_roots = ['Root']
        emf_sort_xmi_attributes = False
        emf_xmi_output_name = "m1_model_out.xmi"
        emf_convert_rst_to_plain = True
        """
    )


def gen_sphinx_needs_conf():
    """Generate the sphinx-needs config part for the Sphinx builder."""
    return textwrap.dedent(
        """\
        extensions = [
            "sphinx_needs",
            "sphinx_emf",
        ]
        needs_types = [
            dict(directive="root", title="Root", prefix="root_", color="#BFD8D2", style="node"),
            dict(directive="sub", title="Sub", prefix="sub_", color="#BFD8D2", style="node"),
            dict(directive="subsub", title="SubSub", prefix="subsub_", color="#BFD8D2", style="node"),
            dict(directive="subsub2", title="SubSub2", prefix="subsub2_", color="#BFD8D2", style="node"),
            dict(directive="subsubsub", title="SubSubSub", prefix="subsubsub_", color="#BFD8D2", style="node"),
        ]
        needs_extra_options = [
            "name",
        ]
        needs_extra_links = [
            {
                "option": "inputs",
                "incoming": "needed by",
                "outgoing": "inputs",
                "copy": False,
            },
        ]
        needs_id_regex = r".*"
        """
    )


def gen_common_conf(ecore_path):
    """Generate the sphinx-emf config part common to CLI and builder."""
    return textwrap.dedent(
        f"""\
        emf_path_m2_model = r"{ecore_path}"
        emf_pre_read_hook = None
        emf_post_read_hook = None
        emf_class_2_need_def = {{
            "Root": {{
                "need_static": {{
                    "type": "root",
                }},
                "emf_to_need_options": [
                    ("_internal_id", "title"),
                    ("_internal_id", "id"),
                ],
                "emf_to_need_content": [
                    ("Subs", "Subs"),
                ],
                "settings": {{
                    "remove_if_unlinked": False,
                }},
            }},
            "Sub": {{
                "need_static": {{
                    "type": "sub",
                }},
                "emf_to_need_options": [
                    ("_internal_id", "title"),
                    ("_internal_id", "id"),
                ],
                "emf_to_need_content": [
                    ("SubSubs", "SubSubs"),
                ],
                "settings": {{
                    "remove_if_unlinked": False,
                }},
            }},
            "SubSub": {{
                "need_static": {{
                    "type": "subsub",
                }},
                "emf_to_need_options": [
                    ("_internal_id", "title"),
                    ("_internal_id", "id"),
                ],
                "emf_to_need_content": [
                    ("SubSubSubs", "SubSubSubs"),
                ],
                "settings": {{
                    "remove_if_unlinked": False,
                }},
            }},
            "SubSub2": {{
                "need_static": {{
                    "type": "subsub2",
                }},
                "emf_to_need_options": [
                    ("_internal_id", "title"),
                    ("_internal_id", "id"),
                ],
                "emf_to_need_content": [
                    ("SubSubSubs", "SubSubSubs"),
                ],
                "settings": {{
                    "remove_if_unlinked": False,
                }},
            }},
            "SubSubSub": {{
                "need_static": {{
                    "type": "subsubsub",
                }},
                "emf_to_need_options": [
                    ("_internal_id", "title"),
                    ("_internal_id", "id"),
                    ("FieldSet", "name"),
                ],
                "emf_to_need_content": [
                ],
                "settings": {{
                    "remove_if_unlinked": False,
                }},
            }},
        }}
        """
    )  # nosec
