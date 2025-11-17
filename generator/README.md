# Generator Engine

A Python-based generation engine for building Ansible playbooks from YAML template libraries using PyYAML and Jinja2.

## Overview

The generator engine provides a structured approach to creating Ansible playbooks by:

1. **Loading YAML Template Library**: Define modules as YAML files with required fields validation
2. **Data Structures**: Python classes representing modules, prompts, and task templates
3. **Template Rendering**: Jinja2-based rendering layer for user-supplied parameters
4. **Playbook Building**: Aggregate multiple modules into complete playbook structures
5. **File Management**: Helper utilities for naming and writing playbooks to disk

## Architecture

### Modules

- **`models.py`**: Data structures (Module, TaskTemplate, Prompt, ValidationError)
- **`templates.py`**: YAML template library loader with validation
- **`renderer.py`**: Jinja2 rendering layer for task dictionaries
- **`builder.py`**: PlaybookBuilder for aggregating modules into playbooks
- **`utils.py`**: Helper utilities for file naming and directory management

### Template Library

YAML template files in `generator/template_library/` define reusable modules with:

- **name**: Module identifier
- **description**: Module purpose
- **prompts**: User input parameters with validation
- **vars**: Template variables
- **tasks**: List of task templates with optional sections (loop, when, notify)
- **handlers**: Event-driven tasks

## Quick Start

### Basic Usage in Python Shell

```python
from generator import PlaybookBuilder

# Create a builder instance
builder = PlaybookBuilder()

# List available modules
modules = builder.list_modules()
print(f"Available modules: {modules}")

# Build a playbook
builder.set_playbook_name("Web Server Setup")
builder.set_hosts("webservers")
builder.add_module('webserver', {
    'server_type': 'nginx',
    'port': 80,
    'enable_ssl': False
})

# Write to file
output_path = builder.write_to_file()
print(f"Playbook written to: {output_path}")
```

### Combining Multiple Modules

```python
from generator import PlaybookBuilder

builder = PlaybookBuilder()
builder.set_playbook_name("Complete Server Setup")
builder.set_hosts("all")

# Add multiple modules
builder.add_module('webserver', {
    'server_type': 'apache2',
    'port': 8080
})

builder.add_module('firewall', {
    'allowed_ports': '22,8080,443',
    'default_policy': 'deny'
})

builder.add_module('user_management', {
    'username': 'deploy',
    'sudo_access': True
})

# Write combined playbook
output_path = builder.write_to_file('server_setup.yml')
```

### Custom Variables

```python
builder = PlaybookBuilder()
builder.set_playbook_name("Custom App Deployment")
builder.set_hosts("app_servers")

# Add custom variables
builder.add_vars({
    'app_name': 'myapp',
    'app_version': '1.2.3',
    'environment': 'production'
})

# Add custom tasks
builder.add_task({
    'name': 'Deploy application',
    'debug': {
        'msg': 'Deploying {{ app_name }} version {{ app_version }}'
    }
})

builder.write_to_file('deployment.yml')
```

### Timestamped Filenames

```python
builder = PlaybookBuilder()
builder.set_playbook_name("Backup Setup")
builder.set_hosts("all")
# ... add modules ...

# Write with timestamp in filename
output_path = builder.write_to_file(timestamped=True)
# Output: generated_playbooks/backup_setup_20231117_143025.yml
```

## Creating Custom Modules

Create a YAML file in `generator/template_library/`:

```yaml
# my_module.yaml
name: my_module
description: Custom module for my use case
prompts:
  - name: parameter_name
    description: Description of the parameter
    type: string
    required: true
    default: default_value
vars:
  my_var: "{{ parameter_name }}"
tasks:
  - name: Task name
    module: ansible_module
    params:
      key: value
      templated_key: "{{ parameter_name }}"
    when: "{{ some_condition }}"
    notify:
      - handler_name
handlers:
  - name: handler_name
    module: service
    params:
      name: my_service
      state: restarted
```

### Prompt Types

- `string`: Text value
- `integer`: Numeric value
- `boolean`: True/False
- `list`: Array of values
- `dict`: Key-value pairs

### Task Optional Sections

- **when**: Conditional execution (Jinja2 expression)
- **loop**: Loop over items (Jinja2 expression)
- **notify**: Trigger handlers (list of handler names)
- **register**: Save task result to variable

## Validation

The engine provides comprehensive validation with actionable error messages:

```python
from generator import PlaybookBuilder, ValidationError

builder = PlaybookBuilder()

try:
    builder.set_playbook_name("Test")
    builder.add_module('database', {})  # Missing required params
except ValidationError as e:
    print(f"Validation error: {e}")
    # Output: Module 'database' missing required parameters: db_name, db_user. 
    #         Please provide values for these fields.
```

### Validation Checks

1. **Module validation**: Required fields, task structure
2. **Prompt validation**: Type checking, required parameters
3. **Playbook validation**: Must have name and at least one task
4. **YAML validation**: Syntax checking when loading templates

## Output Management

### Directory Structure

```
generated_playbooks/
├── my_playbook.yml
├── server_setup.yml
└── backup_20231117_143025.yml
```

### Helper Utilities

```python
from generator.utils import (
    generate_filename,
    ensure_output_dir,
    get_output_path,
    sanitize_filename
)

# Generate filename with timestamp
filename = generate_filename('webserver', timestamped=True)
# Output: webserver_20231117_143025.yml

# Ensure directory exists
output_dir = ensure_output_dir('generated_playbooks')

# Get full output path
path = get_output_path('my_playbook.yml')
# Output: /path/to/generated_playbooks/my_playbook.yml

# Sanitize filename
safe_name = sanitize_filename('My Playbook!')
# Output: my_playbook
```

## Rendering Process

The rendering layer supports:

1. **String templates**: `"{{ variable }}"`
2. **Nested dictionaries**: Recursive rendering
3. **Lists**: Iterative rendering
4. **Jinja2 expressions**: Full Jinja2 syntax support

Example:

```python
from generator import TemplateRenderer, TaskTemplate

renderer = TemplateRenderer()

task = TaskTemplate(
    name="Install {{ package_name }}",
    module="package",
    params={
        "name": "{{ package_name }}",
        "state": "present"
    }
)

rendered = renderer.render_task(task, {'package_name': 'nginx'})
# Output: {
#     'name': 'Install nginx',
#     'package': {'name': 'nginx', 'state': 'present'}
# }
```

## Testing

Run the acceptance tests:

```bash
python test_generator_acceptance.py
```

The test suite covers:
- Basic workflow (load, render, build, write)
- Multiple module aggregation
- Validation with error messages
- Custom variables
- File output verification

## API Reference

### PlaybookBuilder

```python
builder = PlaybookBuilder(library_path=None)
```

**Methods:**

- `set_playbook_name(name)`: Set playbook name
- `set_hosts(hosts)`: Set target hosts pattern
- `set_gather_facts(gather_facts)`: Enable/disable fact gathering
- `add_vars(variables)`: Add custom variables
- `add_module(module_name, parameters)`: Add a module with parameters
- `add_task(task_dict)`: Add a custom task
- `add_handler(handler_dict)`: Add a custom handler
- `build()`: Build playbook structure (returns dict)
- `to_yaml()`: Convert to YAML string
- `write_to_file(output_path, timestamped)`: Write to disk
- `list_modules()`: List available modules
- `get_module_info(module_name)`: Get module details

### TemplateLibrary

```python
library = TemplateLibrary(library_path=None)
```

**Methods:**

- `list_modules()`: List all module names
- `get_module(name)`: Get a module by name
- `validate_required_fields(module_name, parameters)`: Validate parameters
- `add_module(module)`: Add module programmatically
- `reload()`: Reload templates from disk

### TemplateRenderer

```python
renderer = TemplateRenderer()
```

**Methods:**

- `render_value(template_str, context)`: Render a template string
- `render_dict(data, context)`: Render dictionary values
- `render_list(data, context)`: Render list items
- `render_task(task, context)`: Render a task template
- `render_module(module, parameters)`: Render complete module

## Included Modules

### webserver
Install and configure Apache or Nginx web server with port configuration and SSL options.

### database
Set up MySQL or PostgreSQL database with user management and optional backups.

### user_management
Create system users with SSH keys and sudo access.

### firewall
Configure UFW firewall with custom port rules and default policies.

## Acceptance Criteria

✅ **Importing the builder**: `from generator import PlaybookBuilder`  
✅ **Loading templates**: Automatic loading from YAML library with validation  
✅ **Rendering with sample data**: Jinja2 rendering with user parameters  
✅ **Combining modules**: Multiple modules aggregated into single playbook  
✅ **Writing valid YAML**: Syntactically correct playbooks written to disk  
✅ **Helper utilities**: Timestamped filenames and directory management  
✅ **Validation errors**: Actionable error messages for missing/invalid data  

## License

See project root LICENSE file.
