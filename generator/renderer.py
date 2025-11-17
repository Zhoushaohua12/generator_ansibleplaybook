"""Template rendering layer using Jinja2 for task dictionaries."""

from jinja2 import Environment, BaseLoader, TemplateError
from typing import Dict, Any, List
from generator.models import Module, TaskTemplate, ValidationError


class TemplateRenderer:
    """Renders module templates with user-supplied parameters using Jinja2."""
    
    def __init__(self):
        """Initialize the Jinja2 environment."""
        self.env = Environment(loader=BaseLoader())
    
    def render_value(self, template_str: str, context: Dict[str, Any]) -> Any:
        """Render a template string with the given context.
        
        Args:
            template_str: Template string (may contain Jinja2 expressions).
            context: Dictionary of variables for rendering.
            
        Returns:
            Rendered value (string or original type if not a template).
            
        Raises:
            ValidationError: If template rendering fails.
        """
        if not isinstance(template_str, str):
            return template_str
        
        if '{{' not in template_str and '{%' not in template_str:
            return template_str
        
        try:
            template = self.env.from_string(template_str)
            return template.render(**context)
        except TemplateError as e:
            raise ValidationError(f"Template rendering error: {str(e)}")
    
    def render_dict(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively render all values in a dictionary.
        
        Args:
            data: Dictionary to render.
            context: Variables for rendering.
            
        Returns:
            Dictionary with all template strings rendered.
        """
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.render_value(value, context)
            elif isinstance(value, dict):
                result[key] = self.render_dict(value, context)
            elif isinstance(value, list):
                result[key] = self.render_list(value, context)
            else:
                result[key] = value
        return result
    
    def render_list(self, data: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Recursively render all values in a list.
        
        Args:
            data: List to render.
            context: Variables for rendering.
            
        Returns:
            List with all template strings rendered.
        """
        result = []
        for item in data:
            if isinstance(item, str):
                result.append(self.render_value(item, context))
            elif isinstance(item, dict):
                result.append(self.render_dict(item, context))
            elif isinstance(item, list):
                result.append(self.render_list(item, context))
            else:
                result.append(item)
        return result
    
    def render_task(self, task: TaskTemplate, context: Dict[str, Any]) -> Dict[str, Any]:
        """Render a task template with parameters.
        
        Args:
            task: TaskTemplate to render.
            context: User-supplied parameter values and variables.
            
        Returns:
            Task dictionary ready for YAML serialization.
        """
        rendered_params = self.render_dict(task.params, context)
        
        task_dict = {
            'name': self.render_value(task.name, context),
            task.module: rendered_params
        }
        
        if task.when:
            task_dict['when'] = self.render_value(task.when, context)
        
        if task.loop:
            task_dict['loop'] = self.render_value(task.loop, context)
        
        if task.notify:
            task_dict['notify'] = self.render_list(task.notify, context)
        
        if task.register:
            task_dict['register'] = self.render_value(task.register, context)
        
        return task_dict
    
    def render_module(self, module: Module, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Render a complete module with all tasks and handlers.
        
        Args:
            module: Module to render.
            parameters: User-supplied parameter values.
            
        Returns:
            Dictionary containing rendered module data including tasks and handlers.
        """
        context = {}
        
        for prompt in module.prompts:
            if prompt.name in parameters:
                context[prompt.name] = parameters[prompt.name]
            elif prompt.default is not None:
                context[prompt.name] = prompt.default
        
        context.update(module.vars)
        
        rendered_tasks = []
        for task in module.tasks:
            rendered_tasks.append(self.render_task(task, context))
        
        rendered_handlers = []
        for handler in module.handlers:
            rendered_handlers.append(self.render_task(handler, context))
        
        return {
            'name': module.name,
            'description': module.description,
            'tasks': rendered_tasks,
            'handlers': rendered_handlers,
            'vars': self.render_dict(module.vars, context),
            'context': context
        }
