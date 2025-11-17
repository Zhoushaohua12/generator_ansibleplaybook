import os
from typing import Dict, Any
from playbook_generator.renderer import PlaybookRenderer
from playbook_generator.template_loader import TemplateLoader


class PlaybookBuilder:
    """Builds and writes playbooks to disk."""

    def __init__(self, templates_dir: str = None):
        """Initialize the playbook builder.
        
        Args:
            templates_dir: Directory containing templates.
        """
        if templates_dir is None:
            import os
            templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        
        self.templates_dir = templates_dir
        self.renderer = PlaybookRenderer(templates_dir)
        self.loader = TemplateLoader(templates_dir)

    def build_playbook(self, template_name: str, parameters: Dict[str, Any]) -> str:
        """Build a playbook by rendering a template.
        
        Args:
            template_name: Name of the template to use.
            parameters: Dictionary of parameters for the template.
            
        Returns:
            Rendered playbook content.
        """
        return self.renderer.render(template_name, parameters)

    def write_playbook(self, content: str, output_path: str) -> str:
        """Write playbook content to disk.
        
        Args:
            content: Playbook content to write.
            output_path: Path where to write the playbook file.
            
        Returns:
            Absolute path to the written file.
            
        Raises:
            IOError: If write fails.
        """
        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(content)
        
        return output_path

    def build_and_write(self, template_name: str, parameters: Dict[str, Any], 
                       output_path: str) -> str:
        """Build a playbook and write it to disk in one operation.
        
        Args:
            template_name: Name of the template to use.
            parameters: Dictionary of parameters for the template.
            output_path: Path where to write the playbook file.
            
        Returns:
            Absolute path to the written file.
        """
        content = self.build_playbook(template_name, parameters)
        return self.write_playbook(content, output_path)
