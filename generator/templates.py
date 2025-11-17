"""Load and wrap YAML template library with validation for required fields."""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from generator.models import Module, ValidationError


class TemplateLibrary:
    """Manages loading and validation of YAML template library."""
    
    def __init__(self, library_path: Optional[str] = None):
        """Initialize template library.
        
        Args:
            library_path: Path to directory containing YAML template files.
                         Defaults to template_library/ in the generator package.
        """
        if library_path is None:
            library_path = os.path.join(
                os.path.dirname(__file__),
                'template_library'
            )
        self.library_path = library_path
        self._modules: Dict[str, Module] = {}
        self._load_library()
    
    def _load_library(self):
        """Load all YAML template files from the library."""
        if not os.path.exists(self.library_path):
            return
        
        for filename in os.listdir(self.library_path):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                filepath = os.path.join(self.library_path, filename)
                try:
                    self._load_module_file(filepath)
                except Exception as e:
                    raise ValidationError(
                        f"Failed to load template file '{filename}': {str(e)}"
                    )
    
    def _load_module_file(self, filepath: str):
        """Load a single YAML module file.
        
        Args:
            filepath: Path to the YAML file.
            
        Raises:
            ValidationError: If file cannot be loaded or validated.
        """
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValidationError(f"Invalid YAML syntax: {str(e)}")
        except IOError as e:
            raise ValidationError(f"Cannot read file: {str(e)}")
        
        if not data:
            raise ValidationError("YAML file is empty")
        
        if not isinstance(data, dict):
            raise ValidationError("YAML file must contain a dictionary")
        
        module = Module.from_dict(data)
        
        try:
            module.validate()
        except ValidationError as e:
            raise ValidationError(
                f"Validation failed for '{filepath}': {str(e)}"
            )
        
        self._modules[module.name] = module
    
    def list_modules(self) -> List[str]:
        """List all available module names.
        
        Returns:
            Sorted list of module names.
        """
        return sorted(self._modules.keys())
    
    def get_module(self, name: str) -> Module:
        """Get a module by name.
        
        Args:
            name: Name of the module.
            
        Returns:
            Module object.
            
        Raises:
            ValidationError: If module not found.
        """
        if name not in self._modules:
            available = ', '.join(self.list_modules())
            raise ValidationError(
                f"Module '{name}' not found. "
                f"Available modules: {available if available else 'none'}"
            )
        return self._modules[name]
    
    def validate_required_fields(self, module_name: str, parameters: Dict) -> None:
        """Validate that all required fields are present in parameters.
        
        Args:
            module_name: Name of the module.
            parameters: User-provided parameters.
            
        Raises:
            ValidationError: If required fields are missing.
        """
        module = self.get_module(module_name)
        missing_fields = []
        
        for prompt in module.prompts:
            if prompt.required and prompt.name not in parameters:
                if prompt.default is None:
                    missing_fields.append(prompt.name)
        
        if missing_fields:
            raise ValidationError(
                f"Module '{module_name}' missing required parameters: "
                f"{', '.join(missing_fields)}. "
                f"Please provide values for these fields."
            )
    
    def add_module(self, module: Module):
        """Add a module to the library programmatically.
        
        Args:
            module: Module to add.
            
        Raises:
            ValidationError: If module validation fails.
        """
        module.validate()
        self._modules[module.name] = module
    
    def reload(self):
        """Reload all templates from the library directory."""
        self._modules = {}
        self._load_library()
