from docutils import nodes
from sphinx.util.docutils import Directive
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.util.logging import getLogger
from django.core.management import call_command
from io import StringIO
import markdown

logger = getLogger(__name__)


class MyCustomDirective(Directive):
    # Optional: Define the directive name that will be used in reStructuredText
    has_content = True
    required_arguments = 1

    def run(self):
        app_name = self.arguments[0]
        output = StringIO()

        try:
            call_command("modelinfo", app_name, "-v", "2", "-o", "test.html", stdout=output)
            content = output.getvalue()
            html_content = markdown.markdown(content)  # Convert to HTML
        except Exception as e:
            logger.error("Error running modelinfo: %s", e)
            html_content = f"<div class='admonition danger'>Error: {e}</div>"
        finally:
            output.close()

        # Create a raw node with the HTML content
        raw_node = nodes.raw(text=html_content, format="html")

        # Return the raw node so it will be included in the document
        return [raw_node]


def setup(app):
    app.add_directive("mycustomdirective", MyCustomDirective)
