"""PlaybookBuilder that aggregates modules into full playbook structure."""

import yaml
from typing import Dict, Any, List, Optional
from generator.models import Module, ValidationError
from generator.templates import TemplateLibrary
from generator.renderer import TemplateRenderer
from generator.utils import get_output_path, ensure_output_dir


class PlaybookBuilder:
    """Builds complete Ansible playbooks from module templates."""
    
    def __init__(self, library_path: Optional[str] = None):
        """Initialize the playbook builder.
        
        Args:
            library_path: Path to template library directory.
        """
        self.library = TemplateLibrary(library_path)
        self.renderer = TemplateRenderer()
        self._playbook_data = None
        self.reset()
    
    def reset(self):
        """Reset the builder to start a new playbook."""
        self._playbook_data = {
            'name': None,
            'hosts': 'all',
            'gather_facts': True,
            'vars': {},
            'tasks': [],
            'handlers': []
        }
    
    def set_playbook_name(self, name: str) -> 'PlaybookBuilder':
        """Set the playbook name.
        
        Args:
            name: Name for the playbook.
            
        Returns:
            Self for method chaining.
        """
        self._playbook_data['name'] = name
        return self
    
    def set_hosts(self, hosts: str) -> 'PlaybookBuilder':
        """Set target hosts for the playbook.
        
        Args:
            hosts: Host pattern (e.g., 'all', 'webservers', 'db[0]').
            
        Returns:
            Self for method chaining.
        """
        self._playbook_data['hosts'] = hosts
        return self
    
    def set_gather_facts(self, gather_facts: bool) -> 'PlaybookBuilder':
        """Set whether to gather facts.
        
        Args:
            gather_facts: Whether to gather facts.
            
        Returns:
            Self for method chaining.
        """
        self._playbook_data['gather_facts'] = gather_facts
        return self
    
    def add_vars(self, variables: Dict[str, Any]) -> 'PlaybookBuilder':
        """Add variables to the playbook.
        
        Args:
            variables: Dictionary of variables to add.
            
        Returns:
            Self for method chaining.
        """
        self._playbook_data['vars'].update(variables)
        return self
    
    def add_module(self, module_name: str, parameters: Dict[str, Any]) -> 'PlaybookBuilder':
        """Add a module to the playbook with parameters.
        
        Args:
            module_name: Name of the module to add.
            parameters: Parameters for the module.
            
        Returns:
            Self for method chaining.
            
        Raises:
            ValidationError: If module not found or validation fails.
        """
        module = self.library.get_module(module_name)
        
        self.library.validate_required_fields(module_name, parameters)
        
        rendered = self.renderer.render_module(module, parameters)
        
        self._playbook_data['tasks'].extend(rendered['tasks'])
        self._playbook_data['handlers'].extend(rendered['handlers'])
        
        self.add_vars(rendered['vars'])
        
        return self
    
    def add_task(self, task_dict: Dict[str, Any]) -> 'PlaybookBuilder':
        """Add a custom task directly to the playbook.
        
        Args:
            task_dict: Task dictionary ready for YAML serialization.
            
        Returns:
            Self for method chaining.
        """
        self._playbook_data['tasks'].append(task_dict)
        return self
    
    def add_handler(self, handler_dict: Dict[str, Any]) -> 'PlaybookBuilder':
        """Add a custom handler directly to the playbook.
        
        Args:
            handler_dict: Handler dictionary ready for YAML serialization.
            
        Returns:
            Self for method chaining.
        """
        self._playbook_data['handlers'].append(handler_dict)
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the playbook structure.
        
        Returns:
            Complete playbook structure as a dictionary.
            
        Raises:
            ValidationError: If playbook is invalid.
        """
        if not self._playbook_data['name']:
            raise ValidationError(
                "Playbook must have a name. Use set_playbook_name() to set it."
            )
        
        if not self._playbook_data['tasks']:
            raise ValidationError(
                "Playbook must have at least one task. "
                "Use add_module() or add_task() to add tasks."
            )
        
        playbook = {
            'name': self._playbook_data['name'],
            'hosts': self._playbook_data['hosts'],
            'gather_facts': self._playbook_data['gather_facts']
        }
        
        if self._playbook_data['vars']:
            playbook['vars'] = self._playbook_data['vars']
        
        playbook['tasks'] = self._playbook_data['tasks']
        
        if self._playbook_data['handlers']:
            playbook['handlers'] = self._playbook_data['handlers']
        
        return playbook
    
    def to_yaml(self) -> str:
        """Convert the playbook to YAML format.
        
        Returns:
            YAML string representation of the playbook.
        """
        playbook_structure = self.build()
        
        return yaml.dump(
            [playbook_structure],
            default_flow_style=False,
            sort_keys=False,
            explicit_start=True
        )
    
    def write_to_file(self, output_path: str = None, timestamped: bool = False) -> str:
        """Write the playbook to a YAML file.
        
        Args:
            output_path: Path to output file. If None, auto-generates in generated_playbooks/.
            timestamped: Whether to add timestamp to filename.
            
        Returns:
            Absolute path to the written file.
            
        Raises:
            ValidationError: If playbook is invalid.
            IOError: If file cannot be written.
        """
        if output_path is None:
            playbook_name = self._playbook_data.get('name', 'playbook')
            from generator.utils import sanitize_filename
            base_name = sanitize_filename(playbook_name)
            output_path = get_output_path(base_name + '.yml', timestamped=timestamped)
        else:
            import os
            output_dir = os.path.dirname(output_path) or 'generated_playbooks'
            ensure_output_dir(output_dir)
            output_path = os.path.abspath(output_path)
        
        yaml_content = self.to_yaml()
        
        try:
            with open(output_path, 'w') as f:
                f.write(yaml_content)
        except IOError as e:
            raise IOError(f"Failed to write playbook to '{output_path}': {str(e)}")
        
        return output_path
    
    def list_modules(self) -> List[str]:
        """List all available modules in the template library.
        
        Returns:
            List of module names.
        """
        return self.library.list_modules()
    
    def get_module_info(self, module_name: str) -> Module:
        """Get information about a module.
        
        Args:
            module_name: Name of the module.
            
        Returns:
            Module object with full information.
        """
        return self.library.get_module(module_name)
