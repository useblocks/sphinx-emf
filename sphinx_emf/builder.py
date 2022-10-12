"""Builders for sphinx-emf."""

import os
from typing import Iterable, Optional, Set

from docutils import nodes
from sphinx.builders import Builder

from sphinx_emf.ecore.io_ecore import load_m2, save_m1
from sphinx_emf.sphinx_logging import get_logger


log = get_logger(__name__)


class EmfBuilder(Builder):
    """Generate ECore M1 model from RST needs."""

    name = "emf"
    format = "xml"
    file_suffix = ".xml"
    links_suffix = None

    def write_doc(self, docname: str, doctree: nodes.document) -> None:
        """Needed by Sphinx, it does nothing."""
        del docname
        del doctree

    def finish(self) -> None:
        """Generate the M1 model."""
        env = self.env
        config = env.config

        needs = env.needs_all_needs.values()  # We need a list of needs for later filter checks
        del needs

        m2_rset = load_m2(config)
        del m2_rset
        out_path = os.path.join(self.outdir, "ecore_m1.xml")
        save_m1([], out_path)
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
