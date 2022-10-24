"""Functions that can be imported by end users to enable handling of non-RST content input."""


import docutils
from docutils.utils import Reporter


class SilentReporter(Reporter):
    """Disable output to read reporter messages programmatically only."""

    def __init__(
        self, source, report_level, halt_level, stream=None, debug=0, encoding="ascii", error_handler="replace"
    ):
        """Mainly call super."""
        self.messages = []
        Reporter.__init__(self, source, report_level, halt_level, stream, debug, encoding, error_handler)

    def system_message(self, level, message, *children, **kwargs):
        """Add to messages field to evaluate this later."""
        self.messages.append((level, message, children, kwargs))
        return docutils.nodes.system_message(message, level=level, type=self.levels[level], *children, **kwargs)


def escape_inline_literals(text):
    """
    Run input text through docutils RST parser and check for errors.

    This can be used to check whether escaping is necessary.
    """
    src_path = "XMI field input"
    # create a static variable, stolen from https://stackoverflow.com/a/279586
    if "context" not in dir(escape_inline_literals):
        # statically store variables that are needed over and over for better performance
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
                # something else went wrong
                break
        ret_lines.append(new_line)
    return_rst = "\n".join(ret_lines).strip()
    return return_rst


def _split_newlines(input_str):
    r"""
    Split strings by multiple newline sequences such as \n or XML escape sequences.

    Both need to be handled correctly, so the input string is split on all of them.
    """
    newline_sequences = ["\r\n", "\n", "&#xD;&#xA;"]
    magic_seq = "$!$#"
    for sequence in newline_sequences:
        if sequence in input_str:
            input_str = input_str.replace(sequence, magic_seq)
    lines = input_str.split(magic_seq)
    lines = [line.strip() for line in lines]  # remove spaces at beginning and end
    lines = [line for line in lines if line]  # prepend line with indentation if not empty
    return lines
