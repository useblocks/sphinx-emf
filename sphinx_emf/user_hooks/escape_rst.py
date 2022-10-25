"""Functions that can be imported by end users to enable handling of non-RST content input."""


import re
from typing import List, Literal, Tuple

import docutils
from docutils.utils import Reporter


class SilentReporter(Reporter):
    """Disable output to read reporter messages programmatically only."""

    def __init__(
        self, source, report_level, halt_level, stream=None, debug=0, encoding="ascii", error_handler="replace"
    ):
        """Mainly replace defaults."""
        self.messages = []
        Reporter.__init__(self, source, report_level, halt_level, stream, debug, encoding, error_handler)

    def system_message(self, level, message, *children, **kwargs):
        """Add to messages field to evaluate this later."""
        self.messages.append((level, message, children, kwargs))
        return docutils.nodes.system_message(message, level=level, type=self.levels[level], *children, **kwargs)


def escape_inline_literals(text):
    """
    Run input text through docutils RST parser and check for errors.

    This is used to check whether escaping is necessary.
    """
    src_path = "XMI field input"
    # create a static context variable, stolen from https://stackoverflow.com/a/279586
    # it stores variables that are needed in each invocation for better performance
    if "context" not in dir(escape_inline_literals):
        parser = docutils.parsers.rst.Parser()
        settings = docutils.frontend.OptionParser().get_default_values()
        settings.tab_width = 4
        settings.pep_references = None
        settings.rfc_references = None
        reporter = SilentReporter(
            src_path,
            settings.report_level,  # pylint: disable=no-member
            settings.halt_level,  # pylint: disable=no-member
            stream=settings.warning_stream,  # pylint: disable=no-member
            debug=settings.debug,  # pylint: disable=no-member
            encoding=settings.error_encoding,  # pylint: disable=no-member
            error_handler=settings.error_encoding_error_handler,  # pylint: disable=no-member
        )
        document = docutils.nodes.document(settings, reporter, source=src_path)
        # document = docutils.utils.new_document("XMI field input", settings)
        document.note_source(src_path, -1)
        escape_inline_literals.context = {
            "document": document,
            "parser": parser,
            "reporter": reporter,
        }

    escapes = {
        "emphasis": "*",
        "strong": "**",
        "interpreted text or phrase reference": "`",
        "literal": "``",
        # "target": "_`",
        # "footnote_reference": "]_",
        # "substitution_reference": "|",
        # "reference": "_",
        # "anonymous_reference": "__",
    }

    lines = _split_newlines(text)
    ret_lines = []
    for line in lines:
        new_line = line
        while True:
            escape_inline_literals.context["reporter"].messages = []
            escape_inline_literals.context["parser"].parse(new_line, escape_inline_literals.context["document"])
            if not escape_inline_literals.context["reporter"].messages:
                break
            found_msg = False
            for message_tuple in escape_inline_literals.context["reporter"].messages:
                msg = message_tuple[1]
                for symbol_text, symbol in escapes.items():
                    start_text = f"Inline {symbol_text} start-string"
                    if msg.startswith(start_text):
                        found_msg = True
                        new_line = new_line.replace(symbol, f"\\{symbol}")
            if not found_msg:
                # something else went wrong - let this appear later in the build;
                # if the error can be auto-fixed in this library, it should be reported on Github
                break
        ret_lines.append(new_line)
    return_rst = "\n".join(ret_lines).strip()
    return return_rst


def to_rst(text_in):
    """
    Generate valid RST content from plain text input.

    1. incomplete inline literals are escaped
    2. lists are correctly formatted
    3. paragraphs are correctly
    """
    escaped = escape_inline_literals(text_in)
    escaped = escaped.strip()  # remove leading/trailing spaces
    lines = _split_newlines(escaped)

    chunks: List[Tuple[Literal["list", "paragraph"], List[str]]] = []  # tuple str is type, can be list, paragraph
    for idx, line in enumerate(lines):
        force_new_chunk = not bool(line)
        current_type = "list" if (line.startswith("- ") or line.startswith("* ")) else "paragraph"
        last_chunk_type = None
        if chunks:
            if chunks[-1][0] == "list":
                last_chunk_type = "list"
            else:
                last_chunk_type = "paragraph"
        if last_chunk_type == current_type and not force_new_chunk:
            # add it to the last chunk
            chunks[-1][1].append(line)
        else:
            if line:
                chunks.append((current_type, [line]))
            else:
                chunks.append((current_type, []))

    output_lines = []
    for idx, chunk in enumerate(chunks):
        if idx == 0 and len(chunk[1]) == 1 and chunk[0] == "paragraph":
            # one-liner paragraph at the start does not get a newline
            pass
        else:
            # prepend a new line for proper RST format
            output_lines.append("")
        for line in chunk[1]:
            # replace all occurrences of \ with \\ for RST that are not escaped inline literals
            # like \* and \`
            line_new = re.sub(r"(?<![\\\*`])\\(?![\\\*`])", r"\\\\", line)
            line = line_new
            if chunk[0] == "paragraph" and len(chunk[1]) > 1:
                line = f"| {line}"
            output_lines.append(line)

    return_rst = "\n".join(output_lines).rstrip()
    return return_rst


def _split_newlines(input_str):
    r"""
    Split strings by multiple newline sequences such as \n or XML escape sequences.

    Both need to be handled correctly, so the input string is split on all of them.
    """
    # ordered new line sequences by their length (\r\n collapses to \n)
    newline_sequences = ["\r\n", "\r", "\n", "&#xD;&#xA;", "&#xD;", "&#xA;"]
    magic_seq = "$!$#"
    for sequence in newline_sequences:
        if sequence in input_str:
            input_str = input_str.replace(sequence, magic_seq)
    lines = input_str.split(magic_seq)
    lines = [line.rstrip() for line in lines]  # remove spaces at beginning and end
    return lines
