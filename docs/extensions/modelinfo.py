from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.util.logging import getLogger
from django.core.management import call_command
from io import StringIO
import markdown

logger = getLogger(__name__)


class ModelInfo(Directive):
    has_content = False
    required_arguments = 1

    def run(self):
        print("Running modelinfo directive...")
        app_name = self.arguments[0]
        output = StringIO()
        logger.error("Running modelinfo")

        try:
            call_command("modelinfo", app_name, "-v", "2", "--markdown", stdout=output)
            content = output.getvalue()
            html_content = markdown.markdown(content)  # Convert to HTML
        except Exception as e:
            logger.error("Error running modelinfo: %s", e)
            html_content = f"<div class='admonition danger'>Error: {e}</div>"
        finally:
            output.close()

        return [nodes.raw("", html_content, format="html")]


def setup(app):
    app.add_directive("modelinfo", ModelInfo)
    return {"version": "0.1"}

    # print(content)
    # print(type(content))

    # Return a literal block node with the content
    # literal = nodes.literal_block(content, content)
    # literal["language"] = "markdown"  # Syntax highlighting for Markdown
    # return [literal]
    # Inject raw Markdown content
