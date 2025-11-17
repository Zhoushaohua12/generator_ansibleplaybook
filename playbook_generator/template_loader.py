import os
import yaml
from pathlib import Path
from typing import Dict, Any, List


class TemplateLoader:
    """Loads and validates Ansible playbook templates."""

    def __init__(self, templates_dir: str = None):
        """Initialize the template loader.
        
        Args:
            templates_dir: Directory containing template files. Defaults to templates/ in package dir.
        """
        if templates_dir is None:
            templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.templates_dir = templates_dir

    def list_templates(self) -> List[str]:
        """List all available templates.
        
        Returns:
            List of template names (without .j2 extension).
        """
        if not os.path.exists(self.templates_dir):
            return []
        
        templates = []
        for file in os.listdir(self.templates_dir):
            if file.endswith('.j2'):
                templates.append(file[:-3])
        return sorted(templates)

    def load_template(self, template_name: str) -> str:
        """Load a template file.
        
        Args:
            template_name: Name of the template (with or without .j2 extension).
            
        Returns:
            Template content as string.
            
        Raises:
            FileNotFoundError: If template file not found.
        """
        if not template_name.endswith('.j2'):
            template_name = template_name + '.j2'
        
        template_path = os.path.join(self.templates_dir, template_name)
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_name}")
        
        with open(template_path, 'r') as f:
            return f.read()

    def validate_template(self, template_name: str) -> bool:
        """Validate that a template exists and is readable.
        
        Args:
            template_name: Name of the template to validate.
            
        Returns:
            True if valid, False otherwise.
        """
        try:
            self.load_template(template_name)
            return True
        except (FileNotFoundError, IOError):
            return False

    def get_template_schema(self, template_name: str) -> Dict[str, Any]:
        """Get the schema/parameters required for a template.
        
        Args:
            template_name: Name of the template.
            
        Returns:
            Dictionary containing template schema metadata.
        """
        schema_name = template_name.replace('.j2', '') + '_schema.yaml'
        schema_path = os.path.join(self.templates_dir, schema_name)
        
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                return yaml.safe_load(f) or {}
        
        return {}
