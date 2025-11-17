# Ansible Module Templates Catalogue

This directory contains the `ansible_modules.yaml` file - a comprehensive catalogue of Ansible modules with metadata, parameter definitions, and Jinja2 task templates for the playbook generator.

## Overview

The `ansible_modules.yaml` file serves as a reference library that:

1. **Catalogues Ansible Modules**: Groups modules by category (system, file, network, other)
2. **Defines Module Metadata**: Includes human-readable names, descriptions, and Ansible module names
3. **Specifies Parameters**: Documents required and optional parameters for each module
4. **Provides Task Templates**: Includes reusable Jinja2 templates for generating Ansible tasks
5. **Supports Advanced Features**: Enables conditionals, loops, handlers, and variable references

## File Structure

```yaml
modules:
  - name: module_id              # Unique identifier (e.g., 'user', 'package')
    human_name: Display Name     # Human-readable name for UI
    description: Purpose...      # What this module does
    ansible_module: module_name  # Official Ansible module name
    default_task_name: "..."     # Default pattern for task naming
    category: system             # Category: system, file, network, other
    handlers:                    # List of potential handler names
      - handler_name
    prompts:                     # User input parameters
      - name: param_name
        description: "..."
        type: string|integer|boolean|list|dict
        required: true|false
        default: value
        choices: [option1, option2]  # Optional, for enum parameters
    task_template: |             # Jinja2 template for task generation
      name: {{ default_task_name }}
      module_name:
        param: {{ param_name }}
```

## Module Categories

### System (7 modules)
- **user**: Create and manage system users
- **group**: Create and manage system groups
- **service**: Start, stop, restart, and enable system services
- **package**: Install, upgrade, and remove packages (generic)
- **yum**: YUM package management (Red Hat/CentOS/Fedora)
- **apt**: APT package management (Debian/Ubuntu)
- **systemd**: Manage systemd services with advanced options

### File (7 modules)
- **file**: Manage file properties (permissions, ownership, state)
- **copy**: Copy files to remote hosts
- **lineinfile**: Ensure specific lines are present/absent in files
- **replace**: Replace content patterns in files
- **blockinfile**: Insert/remove blocks of lines with markers
- **template**: Deploy files using Jinja2 templating
- **stat**: Gather file/directory statistics

### Network (2 modules)
- **firewalld**: Configure firewalld firewall rules
- **iptables**: Manage IPTables firewall rules

### Other (6 modules)
- **command**: Execute commands without shell processing
- **shell**: Execute shell commands with pipe/redirect support
- **debug**: Print debug messages and variables
- **set_fact**: Set/update facts and variables
- **include_tasks**: Include and execute external task files
- **notify**: Trigger handlers (meta-control)

## Prompt Types

Parameters can be one of the following types:

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text value | `"nginx"`, `"/etc/config.conf"` |
| `integer` | Numeric value | `80`, `1024` |
| `boolean` | True/False | `true`, `false` |
| `list` | Array of values | `[item1, item2]` |
| `dict` | Key-value pairs | `{key1: val1, key2: val2}` |

## Jinja2 Template Features

Task templates support full Jinja2 syntax:

### Variable Substitution
```jinja2
name: {{ default_task_name }}
module_name:
  key: {{ parameter_name }}
```

### Conditionals (if parameter is provided)
```jinja2
{% if owner %}owner: {{ owner }}{% endif %}
```

### Loops (for list parameters)
```jinja2
{% for item in items %}
  - {{ item }}
{% endfor %}
```

### Filters (transform values)
```jinja2
{{ enabled | lower }}     # Convert to lowercase
{{ name | upper }}        # Convert to uppercase
{{ value | indent(2) }}   # Indent multi-line values
```

### Multi-line Blocks
```jinja2
block: |
  {{ content | indent(2) }}
```

## Loading and Using the Catalogue

### Loading with PyYAML

```python
import yaml

with open('templates/ansible_modules.yaml', 'r') as f:
    catalogue = yaml.safe_load(f)

modules = catalogue['modules']
for module in modules:
    print(f"{module['name']}: {module['human_name']}")
```

### Extracting Module Metadata

```python
# Find a specific module
user_module = next(m for m in modules if m['name'] == 'user')

# Get metadata
name = user_module['name']
display_name = user_module['human_name']
description = user_module['description']
category = user_module['category']
ansible_module = user_module['ansible_module']

# Get parameters
prompts = user_module['prompts']
required_params = [p for p in prompts if p.get('required', True)]
optional_params = [p for p in prompts if not p.get('required', False)]
```

### Rendering Task Templates with Jinja2

```python
from jinja2 import Template

# Get module
user_module = next(m for m in modules if m['name'] == 'user')

# Get template
template_str = user_module['task_template']
template = Template(template_str)

# Render with user parameters
context = {
    'default_task_name': 'Create deploy user',
    'username': 'deploy',
    'groups': 'sudo,docker',
    'shell': '/bin/bash',
    'state': 'present',
    'home': None,  # Skip if None
    'uid': None,
    'createhome': True
}

rendered_task = template.render(context)
print(rendered_task)
```

## Extending the Catalogue

To add a new module to the catalogue:

1. **Choose a Category**: system, file, network, or other
2. **Define Module Metadata**:
   - `name`: Unique identifier (lowercase, underscore-separated)
   - `human_name`: Display name for UI
   - `description`: What the module does and when to use it
   - `ansible_module`: Official Ansible module name (can be null for meta-modules)
   - `default_task_name`: Default task name pattern
   - `category`: One of the four categories above

3. **List Handlers** (if applicable):
   - Specify potential event names that other tasks can notify

4. **Define Prompts**:
   - For each parameter, specify name, description, type, required, default
   - Use `choices` for enum parameters
   - Keep prompts focused on user-configurable aspects

5. **Create Task Template**:
   - Use Jinja2 syntax with prompt names as variables
   - Include conditionals for optional parameters: `{% if param_name %}...{% endif %}`
   - Use appropriate filters: `| lower`, `| upper`, `| indent(2)`
   - Maintain valid YAML indentation in rendered output

### Example: Adding an HTTP Module

```yaml
- name: http_request
  human_name: HTTP Request
  description: Make HTTP requests to URLs with custom headers and methods
  ansible_module: uri
  default_task_name: "HTTP request to {{ url }}"
  category: network
  handlers: []
  prompts:
    - name: url
      description: URL to request
      type: string
      required: true
      default: null
    - name: method
      description: HTTP method (GET, POST, PUT, DELETE)
      type: string
      required: false
      default: GET
      choices: [GET, POST, PUT, DELETE]
    - name: body
      description: Request body (JSON or text)
      type: string
      required: false
      default: null
    - name: status_code
      description: Expected HTTP status code
      type: integer
      required: false
      default: 200
  task_template: |
    name: {{ default_task_name }}
    uri:
      url: {{ url }}
      method: {{ method }}
      status_code: {{ status_code }}
      {% if body %}body: {{ body }}{% endif %}
```

## Validation Rules

The catalogue enforces these validation rules:

1. **Required Metadata**: Every module must have name, human_name, description, ansible_module, default_task_name, category
2. **Valid Prompt Types**: Only string, integer, boolean, list, or dict
3. **Task Template Structure**: Must be a Jinja2 template string that produces valid YAML
4. **YAML Compliance**: File must be valid YAML with proper indentation
5. **Unique Module Names**: Each module name must be unique within the catalogue

## Usage in the Generator Engine

The generator engine uses this catalogue to:

1. **Load Available Modules**: Display list of available modules
2. **Get Module Info**: Show prompts and metadata to users
3. **Validate Parameters**: Check that user-provided parameters match prompt definitions
4. **Render Tasks**: Convert templates + parameters into Ansible task YAML
5. **Build Playbooks**: Aggregate multiple rendered tasks into complete playbooks

Example integration:

```python
from generator import PlaybookBuilder
import yaml

# Load catalogue
with open('templates/ansible_modules.yaml', 'r') as f:
    catalogue = yaml.safe_load(f)

# User selects modules and provides parameters
builder = PlaybookBuilder()
builder.set_playbook_name("Web Server Setup")
builder.set_hosts("webservers")

# Add modules using catalogue definitions
builder.add_module('apt', {
    'package_name': 'nginx',
    'state': 'latest',
    'update_cache': True
})

builder.add_module('systemd', {
    'service_name': 'nginx',
    'state': 'started',
    'enabled': True
})

# Write the generated playbook
output = builder.write_to_file()
```

## Testing the Catalogue

To validate the catalogue:

```bash
python3 << 'EOF'
import yaml

with open('templates/ansible_modules.yaml', 'r') as f:
    data = yaml.safe_load(f)

# Check structure
assert 'modules' in data
assert isinstance(data['modules'], list)

# Validate each module
for module in data['modules']:
    assert 'name' in module
    assert 'prompts' in module
    assert 'task_template' in module
    
    # Check prompt types
    for prompt in module['prompts']:
        assert prompt['type'] in ['string', 'integer', 'boolean', 'list', 'dict']

print("✓ All validation checks passed!")
EOF
```

## Performance Notes

- The catalogue contains 22 modules across 4 categories
- Loads successfully with PyYAML's `safe_load()`
- Each module is self-contained and can be loaded independently
- Templates render efficiently with Jinja2
- ~5KB file size, minimal memory footprint

## Integration Points

This catalogue integrates with:

- **Generator Engine** (`generator/`): Loads modules for playbook generation
- **CLI Tools** (`playbook_generator/cli.py`): Lists available modules and their options
- **UI Systems**: Provides metadata for dynamic form generation
- **Documentation**: Can be parsed to generate help text and API documentation

## Support for Advanced Features

### When Conditions
Modules support conditional execution using Jinja2:
```jinja2
{% if condition %}when: "{{ condition }}"{% endif %}
```

### Loop Support
Modules can iterate over lists:
```jinja2
loop: "{{ items | split(',') }}"
```

### Notify Handlers
Modules can trigger handlers:
```jinja2
notify:
  - handler_name
```

### Variable Registration
Modules can register results:
```jinja2
{% if register_as %}register: {{ register_as }}{% endif %}
```

## References

- [Ansible Modules Documentation](https://docs.ansible.com/ansible/latest/modules/modules_by_category.html)
- [Jinja2 Template Engine](https://jinja.palletsprojects.com/)
- [YAML Specification](https://yaml.org/spec/1.2/spec.html)
- [Project Generator Engine](../generator/README.md)
