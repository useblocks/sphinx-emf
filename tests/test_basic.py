"""Test basic app functionality."""
import logging
import os
import textwrap

from click.testing import CliRunner

from sphinx_emf.cli import run


DIR_THIS_FILE = os.path.dirname(os.path.realpath(__file__))


def test_cli(tmp_path, caplog):
    """Check whether main function runs through."""
    caplog.set_level(logging.DEBUG)

    conf_file = tmp_path / "config.py"

    data_path = os.path.abspath(os.path.join(DIR_THIS_FILE, "data", "base"))
    ecore_path = os.path.join(data_path, "base_test.ecore")
    xmi_path = os.path.join(data_path, "base_test.xmi")
    templates_path = os.path.join(data_path, "templates")
    rst_out_path = str(tmp_path / "out.rst")

    config_common = textwrap.dedent(
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
    )
    config_cli = textwrap.dedent(
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
    config = config_common + config_cli
    conf_file.write_text(config)
    runner = CliRunner()
    response = runner.invoke(run, [str(conf_file)])
    assert response.exit_code == 0  # nosec
