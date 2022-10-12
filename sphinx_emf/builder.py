"""Builders for sphinx-emf."""

import os
from typing import Iterable, Optional, Set

from docutils import nodes
from sphinx.builders import Builder

from sphinx_emf.config.invert import invert_emf_class_2_need_def
from sphinx_emf.ecore.io_ecore import load_m2, save_m1
from sphinx_emf.sphinx_logging import get_logger


log = get_logger(__name__)


class EmfBuilder(Builder):
    """Generate ECore M1 model from RST needs."""

    name = "emf"
    format = "xmi"  # noqa: F841
    file_suffix = ".ecore"  # noqa: F841
    links_suffix = None  # noqa: F841

    def write_doc(self, docname: str, doctree: nodes.document) -> None:
        """Needed by Sphinx, it does nothing."""
        del docname
        del doctree

    def finish(self) -> None:
        """Generate the M1 model."""
        env = self.env
        config = env.config

        need_id_2_need = env.needs_all_needs
        m2_rset = load_m2(config)
        mm_root = m2_rset.resources[config.emf_path_m2_model].contents[0]

        inverted_config = invert_emf_class_2_need_def(config.emf_class_2_need_def)

        root_instances = []
        for emf_root in config.emf_model_roots:
            # get the root need
            root_need = None
            for need in need_id_2_need.values():
                need_emf_type = inverted_config["need_type_2_emf_def"][need["type"]]["type"]
                if emf_root == need_emf_type:
                    root_need = need
                    break
            if root_need is None:
                raise RuntimeError(f"Could not find need for EMF root {emf_root}")
            e_class = mm_root.getEClassifier(emf_root)
            if e_class is None:
                log.error(f"Cannot find ECore class for classifier {emf_root}")
                continue
            e_instance = e_class()
            e_instance._internal_id = root_need["xmi_id"]
            e_instance.RiskLevel = mm_root.getEClassifier("RiskLevel").from_string(root_need["risklevel"])
            e_instance.Name = root_need["title"]
            e_instance.Description = root_need["title"]
            e_class_tool = mm_root.getEClassifier("Tool")
            tool = e_class_tool()
            tool._internal_id = "foo"
            tool.Name = "Some tool"
            e_instance.Tools.append(tool)
            root_instances.append(e_instance)

        out_path = os.path.join(self.outdir, "ecore_m1.xmi")
        save_m1(root_instances, out_path)
        log.info("EMF M1 model successfully exported")

    def get_outdated_docs(self) -> Iterable[str]:
        """Needed by Sphinx, it does nothing."""
        return []

    def prepare_writing(self, _docnames: Set[str]) -> None:
        """Needed by Sphinx, it does nothing."""

    def write_doc_serialized(self, _docname: str, _doctree: nodes.document) -> None:
        """Needed by Sphinx, it does nothing."""

    def cleanup(self) -> None:
        """Needed by Sphinx, it does nothing."""

    def get_target_uri(self, _docname: str, _typ: Optional[str] = None) -> str:
        """Needed by Sphinx, it does nothing."""
        return ""
