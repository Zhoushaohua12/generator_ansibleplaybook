from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from typing import Dict, Any


class PlaybookRenderer:
    """Renders Jinja2 templates with parameters to generate playbooks."""

    def __init__(self, templates_dir: str):
        """Initialize the renderer with a templates directory.
        
        Args:
            templates_dir: Directory containing Jinja2 templates.
        """
        self.env = Environment(loader=FileSystemLoader(templates_dir))

    def render(self, template_name: str, parameters: Dict[str, Any]) -> str:
        """Render a template with given parameters.
        
        Args:
            template_name: Name of the template file (with or without .j2 extension).
            parameters: Dictionary of parameters to pass to the template.
            
        Returns:
            Rendered template as string.
            
        Raises:
            TemplateNotFound: If template file not found.
        """
        if not template_name.endswith('.j2'):
            template_name = template_name + '.j2'
        
        template = self.env.get_template(template_name)
        return template.render(**parameters)
