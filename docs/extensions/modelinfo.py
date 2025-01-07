from docutils import nodes
from docutils.parsers.rst import Directive
import subprocess
from sphinx.util.logging import getLogger
from django.core.management import call_command
from io import StringIO

logger = getLogger(__name__)


class ModelInfo(Directive):
    """
    Custom directive to include Django model information dynamically.
    Usage:
    ```{modelinfo} app_name
    ```
    """

    has_content = False
    required_arguments = 1  # The app_name is required
    optional_arguments = 0

    def run(self):
        app_name = self.arguments[0]
        output = StringIO()
        try:
            # Call the Django management command
            call_command("modelinfo", app_name, "-v", "2", "--markdown", stdout=output)
            content = output.getvalue()
        except Exception as e:
            error_message = f"Error running modelinfo command for app '{app_name}': {e}"
            logger.error(error_message)
            content = error_message
        finally:
            output.close()

        # print(content)
        # print(type(content))

        # Return a literal block node with the content
        # literal = nodes.literal_block(content, content)
        # literal["language"] = "markdown"  # Syntax highlighting for Markdown
        # return [literal]
        # Inject raw Markdown content
        raw_node = nodes.raw("", content, format="markdown")
        return [raw_node]


def setup(app):
    app.add_directive("modelinfo", ModelInfo)
