"""Builders for sphinx-emf."""

import os
from typing import Iterable, Optional, Set

from docutils import nodes
from pyecore.ecore import EEnumLiteral, EOrderedSet
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
            root_instances.append(e_instance)
            walk_create_ecore(
                root_need,
                e_instance,
                need_id_2_need,
                config.emf_class_2_need_def,
                inverted_config,
                mm_root,
            )

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


def walk_create_ecore(need, e_instance, need_id_2_need, emf_class_2_need_def, inverted_config, mm_root):
    """Recursively walk the needs and create ECore instances."""
    curr_emf_type = inverted_config["need_type_2_emf_def"][need["type"]]["type"]
    definition = emf_class_2_need_def[curr_emf_type]
    for option, need_def in definition["options"].items():
        if isinstance(need_def, str):
            need_field = need_def
        else:
            need_field = need_def[0]
        emf_field = getattr(e_instance, option)
        if emf_field is None:
            setattr(e_instance, option, need[need_field])
        elif isinstance(emf_field, str):
            setattr(e_instance, option, str(need[need_field]))
        elif isinstance(emf_field, bool):
            setattr(e_instance, option, need[need_field].lower() == "true")
        elif isinstance(emf_field, int):
            setattr(e_instance, option, int(need[need_field]))
        elif isinstance(emf_field, EEnumLiteral):
            enum_value = mm_root.getEClassifier(option).from_string(need[need_field])
            setattr(e_instance, option, enum_value)
        elif isinstance(emf_field, EOrderedSet):
            for link_need_id in need[need_field]:
                linked_need = need_id_2_need[link_need_id]
                local_emf_type = inverted_config["need_type_2_emf_def"][linked_need["type"]]["type"]
                e_class = mm_root.getEClassifier(local_emf_type)
                if e_class is None:
                    log.error(f"Cannot find ECore class for classifier {local_emf_type}")
                    continue
                local_e_instance = e_class()
                emf_field.append(local_e_instance)
                walk_create_ecore(
                    linked_need,
                    local_e_instance,
                    need_id_2_need,
                    emf_class_2_need_def,
                    inverted_config,
                    mm_root,
                )
        else:
            raise ValueError(f"Unexpected EMF field type {type(emf_field)} for need id {need['id']}")
    for option, need_def in definition["contents"].items():
        pass
        # TODO implement me, analyse the docutils nodes
