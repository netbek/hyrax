import cStringIO
import csv
import inspect

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


def get_function_source(fn):
    src = inspect.getsource(fn)
    lines = src.splitlines()

    # Get indentation
    line = lines[1]
    indent = len(line) - len(line.lstrip())

    output = []
    count = len(lines)
    for i, line in enumerate(lines):
        # Ignore function declaration and final return statement
        if i == 0 or i == count - 1:
            continue
        # Strip indentation
        output.append(line[indent:])

    code = '\n'.join(output).strip()
    lexer = PythonLexer()
    formatter = HtmlFormatter(noclasses=True)
    code = highlight(code, lexer, formatter)

    return code


def to_csv(data, fieldnames):
    output = cStringIO.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    contents = output.getvalue()
    output.close()

    return contents
