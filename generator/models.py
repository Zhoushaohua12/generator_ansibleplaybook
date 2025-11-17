"""Data structures for modules, prompts, and task templates."""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class ValidationError(Exception):
    """Exception raised when validation fails with actionable messages."""
    pass


@dataclass
class Prompt:
    """Represents a user input prompt for collecting parameter values."""
    name: str
    description: str
    type: str = "string"
    required: bool = True
    default: Any = None
    
    def validate(self):
        """Validate prompt configuration."""
        if not self.name:
            raise ValidationError("Prompt must have a name")
        if not self.description:
            raise ValidationError(f"Prompt '{self.name}' must have a description")
        valid_types = ["string", "integer", "boolean", "list", "dict"]
        if self.type not in valid_types:
            raise ValidationError(
                f"Prompt '{self.name}' has invalid type '{self.type}'. "
                f"Must be one of: {', '.join(valid_types)}"
            )


@dataclass
class TaskTemplate:
    """Represents a task template with optional sections (loop, when, notify)."""
    name: str
    module: str
    params: Dict[str, Any] = field(default_factory=dict)
    when: Optional[str] = None
    loop: Optional[str] = None
    notify: Optional[List[str]] = None
    register: Optional[str] = None
    
    def validate(self):
        """Validate task template configuration."""
        if not self.name:
            raise ValidationError("Task template must have a name")
        if not self.module:
            raise ValidationError(f"Task template '{self.name}' must specify a module")
        if not isinstance(self.params, dict):
            raise ValidationError(
                f"Task template '{self.name}' params must be a dictionary, "
                f"got {type(self.params).__name__}"
            )
        if self.notify and not isinstance(self.notify, list):
            raise ValidationError(
                f"Task template '{self.name}' notify must be a list, "
                f"got {type(self.notify).__name__}"
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task template to dictionary format for YAML serialization."""
        task_dict = {
            'name': self.name,
            self.module: self.params
        }
        if self.when:
            task_dict['when'] = self.when
        if self.loop:
            task_dict['loop'] = self.loop
        if self.notify:
            task_dict['notify'] = self.notify
        if self.register:
            task_dict['register'] = self.register
        return task_dict


@dataclass
class Module:
    """Represents a module template with prompts and tasks."""
    name: str
    description: str
    prompts: List[Prompt] = field(default_factory=list)
    tasks: List[TaskTemplate] = field(default_factory=list)
    vars: Dict[str, Any] = field(default_factory=dict)
    handlers: List[TaskTemplate] = field(default_factory=list)
    
    def validate(self):
        """Validate module configuration with actionable error messages."""
        if not self.name:
            raise ValidationError("Module must have a name")
        if not self.description:
            raise ValidationError(f"Module '{self.name}' must have a description")
        
        for i, prompt in enumerate(self.prompts):
            try:
                prompt.validate()
            except ValidationError as e:
                raise ValidationError(
                    f"Module '{self.name}', prompt #{i+1}: {str(e)}"
                )
        
        if not self.tasks:
            raise ValidationError(
                f"Module '{self.name}' must have at least one task. "
                "Add tasks to make this module useful."
            )
        
        for i, task in enumerate(self.tasks):
            try:
                task.validate()
            except ValidationError as e:
                raise ValidationError(
                    f"Module '{self.name}', task #{i+1}: {str(e)}"
                )
        
        for i, handler in enumerate(self.handlers):
            try:
                handler.validate()
            except ValidationError as e:
                raise ValidationError(
                    f"Module '{self.name}', handler #{i+1}: {str(e)}"
                )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Module':
        """Create a Module from a dictionary (loaded from YAML)."""
        prompts = [
            Prompt(**prompt_data)
            for prompt_data in data.get('prompts', [])
        ]
        
        tasks = []
        for task_data in data.get('tasks', []):
            tasks.append(TaskTemplate(**task_data))
        
        handlers = []
        for handler_data in data.get('handlers', []):
            handlers.append(TaskTemplate(**handler_data))
        
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            prompts=prompts,
            tasks=tasks,
            vars=data.get('vars', {}),
            handlers=handlers
        )
