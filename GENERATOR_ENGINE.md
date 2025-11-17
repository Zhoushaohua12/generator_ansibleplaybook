# Generator Engine Implementation

## Overview

This document describes the implementation of the generation engine as specified in the ticket requirements.

## Implementation Summary

The generator engine has been successfully implemented under the `generator/` directory with the following components:

### Directory Structure

```
generator/
├── __init__.py              # Package initialization and exports
├── models.py                # Data structures (Module, TaskTemplate, Prompt)
├── templates.py             # YAML template library loader with validation
├── renderer.py              # Jinja2 rendering layer for task dictionaries
├── builder.py               # PlaybookBuilder for aggregating modules
├── utils.py                 # Helper utilities (naming, directory management)
├── README.md                # Comprehensive documentation
└── template_library/        # YAML template files
    ├── webserver.yaml       # Web server installation module
    ├── database.yaml        # Database setup module
    ├── user_management.yaml # User and SSH key management
    └── firewall.yaml        # UFW firewall configuration
```

### Output Directory

```
generated_playbooks/         # All generated playbooks written here
├── *.yml                    # Generated playbook files
└── *_YYYYMMDD_HHMMSS.yml   # Timestamped playbook files
```

## Ticket Requirements ✅

### 1. Python Modules under `generator/`

✅ **Created the following modules:**
- `templates.py` - YAML template library loader
- `builder.py` - PlaybookBuilder class
- `models.py` - Data structures and classes
- `renderer.py` - Jinja2 rendering layer
- `utils.py` - Helper utilities

### 2. Load YAML Template Library with PyYAML

✅ **Implemented in `templates.py`:**
- `TemplateLibrary` class loads YAML files from `template_library/`
- Automatic loading and caching of all `.yaml` and `.yml` files
- PyYAML safe_load for secure parsing
- Error handling for malformed YAML

### 3. Validation for Required Fields

✅ **Comprehensive validation implemented:**
- **Module validation**: Checks for required fields (name, description, tasks)
- **Prompt validation**: Type checking (string, integer, boolean, list, dict)
- **Task validation**: Module and parameter structure verification
- **Parameter validation**: Required field checking with actionable error messages

**Example validation errors:**
```python
ValidationError: Module 'database' missing required parameters: db_name, db_user. 
                 Please provide values for these fields.

ValidationError: Module 'test_module' must have at least one task. 
                 Add tasks to make this module useful.

ValidationError: Prompt 'test' has invalid type 'invalid'. 
                 Must be one of: string, integer, boolean, list, dict
```

### 4. Data Structures/Classes

✅ **Implemented in `models.py`:**

**`Prompt`** - Represents user input prompts:
- `name`: Parameter identifier
- `description`: User-facing description
- `type`: Data type (string, integer, boolean, list, dict)
- `required`: Whether parameter is mandatory
- `default`: Default value if not provided

**`TaskTemplate`** - Represents task templates with optional sections:
- `name`: Task name (supports Jinja2 templates)
- `module`: Ansible module name
- `params`: Module parameters dictionary
- `when`: Optional conditional expression
- `loop`: Optional loop expression
- `notify`: Optional list of handlers to notify
- `register`: Optional variable to register result

**`Module`** - Represents complete module definitions:
- `name`: Module identifier
- `description`: Module purpose
- `prompts`: List of Prompt objects
- `tasks`: List of TaskTemplate objects
- `vars`: Template variables dictionary
- `handlers`: List of handler TaskTemplate objects

**`ValidationError`** - Exception for validation failures with actionable messages

### 5. Template Rendering Layer Using Jinja2

✅ **Implemented in `renderer.py`:**

**`TemplateRenderer`** class provides:
- `render_value()`: Render single template strings
- `render_dict()`: Recursively render dictionary values
- `render_list()`: Recursively render list items
- `render_task()`: Render TaskTemplate to task dictionary
- `render_module()`: Render complete module with all tasks and handlers

**Jinja2 support:**
- Full Jinja2 template syntax in YAML values
- Variable substitution: `"{{ variable }}"`
- Expressions: `"{{ port * 2 }}"`
- Filters: `"{{ name | upper }}"`
- Control structures in YAML (when, loop)

### 6. Support for Optional Sections

✅ **Fully implemented support for:**

**`loop`** - Iterate over items:
```yaml
tasks:
  - name: Allow ports
    module: ufw
    params:
      rule: allow
      port: "{{ item }}"
    loop: "{{ allowed_ports.split(',') }}"
```

**`when`** - Conditional execution:
```yaml
tasks:
  - name: Configure SSL
    module: template
    params:
      src: ssl.conf.j2
      dest: /etc/ssl/config
    when: "{{ enable_ssl }}"
```

**`notify`** - Trigger handlers:
```yaml
tasks:
  - name: Update config
    module: lineinfile
    params:
      path: /etc/app/config
      line: "{{ config_line }}"
    notify:
      - restart service
      - reload config
```

### 7. Task Dictionaries Ready for YAML Serialization

✅ **Task rendering produces proper dictionary structures:**

Input TaskTemplate:
```python
TaskTemplate(
    name="Install {{ package }}",
    module="package",
    params={"name": "{{ package }}", "state": "present"},
    notify=["restart {{ package }}"]
)
```

Output dictionary:
```python
{
    'name': 'Install nginx',
    'package': {
        'name': 'nginx',
        'state': 'present'
    },
    'notify': ['restart nginx']
}
```

### 8. PlaybookBuilder Implementation

✅ **Implemented in `builder.py`:**

**Core functionality:**
- **Aggregate modules**: `add_module(name, parameters)`
- **Full playbook structure**: hosts, vars, tasks, handlers
- **Custom variables**: `add_vars(variables)`
- **Custom tasks**: `add_task(task_dict)` and `add_handler(handler_dict)`
- **Build playbook**: `build()` returns complete structure
- **YAML conversion**: `to_yaml()` produces formatted YAML
- **Write to disk**: `write_to_file(path, timestamped)`

**Builder methods support chaining:**
```python
builder = (PlaybookBuilder()
    .set_playbook_name("Production Setup")
    .set_hosts("production")
    .add_vars({"environment": "prod"})
    .add_module('webserver', params)
    .add_module('firewall', params))
```

**Output structure:**
```yaml
---
- name: Production Setup
  hosts: production
  gather_facts: true
  vars:
    environment: prod
    # ... module vars ...
  tasks:
    # ... aggregated tasks from all modules ...
  handlers:
    # ... aggregated handlers from all modules ...
```

### 9. Write Formatted YAML to `generated_playbooks/`

✅ **Implemented:**
- All playbooks written to `generated_playbooks/` directory
- Directory automatically created if missing
- YAML formatting with `yaml.dump()`:
  - `default_flow_style=False` for readable output
  - `sort_keys=False` to preserve order
  - `explicit_start=True` for `---` document start
- Absolute path resolution
- Returns absolute path to written file

### 10. Helper Utilities

✅ **Implemented in `utils.py`:**

**`generate_filename(base_name, timestamped, extension)`**
- Generate output filenames
- Optional timestamp: `playbook_20231117_143025.yml`
- Custom extensions: `.yml`, `.yaml`

**`ensure_output_dir(directory)`**
- Create output directory if missing
- Returns absolute path
- Uses `os.makedirs(exist_ok=True)`

**`get_output_path(filename, directory, timestamped)`**
- Combine directory and filename
- Ensure directory exists
- Support timestamped filenames

**`sanitize_filename(name)`**
- Convert strings to safe filenames
- Handle spaces, special characters
- Lowercase conversion: `"My Playbook"` → `"my_playbook"`

## Acceptance Criteria Verification

### ✅ Importing the builder in Python shell

```python
from generator import PlaybookBuilder
builder = PlaybookBuilder()
```

### ✅ Loading templates

```python
modules = builder.list_modules()
# Output: ['database', 'firewall', 'user_management', 'webserver']

module = builder.get_module_info('webserver')
# Output: Module(name='webserver', description='Install and configure...', ...)
```

### ✅ Rendering a module with sample data

```python
builder.set_playbook_name("Web Server Setup")
builder.set_hosts("webservers")
builder.add_module('webserver', {
    'server_type': 'nginx',
    'port': 80,
    'enable_ssl': False
})
```

### ✅ Combining multiple tasks into playbook structure

```python
builder.add_module('firewall', {'allowed_ports': '22,80,443'})
builder.add_module('user_management', {'username': 'deploy'})

playbook = builder.build()
# Output: Complete playbook structure with all tasks aggregated
```

### ✅ Writing syntactically valid playbook file

```python
output_path = builder.write_to_file()
# Output: /path/to/generated_playbooks/web_server_setup.yml

# Verify validity
import yaml
with open(output_path, 'r') as f:
    content = yaml.safe_load(f)
# No errors - valid YAML!
```

## Testing

### Test Coverage

**38 new tests** added in `tests/test_generator.py`:
- Model validation tests (7 tests)
- Template library tests (6 tests)
- Renderer tests (5 tests)
- PlaybookBuilder tests (14 tests)
- Utility function tests (6 tests)

**All 78 tests pass** (40 original + 38 new):
```bash
$ pytest -v
============================== 78 passed in 0.87s ==============================
```

### Acceptance Tests

**Comprehensive acceptance test suite** in `test_generator_acceptance.py`:
- Basic workflow test
- Multiple module aggregation test
- Validation error handling test
- Custom variables test

All acceptance tests pass:
```bash
$ python test_generator_acceptance.py
🎉 All acceptance tests passed! 🎉
Total: 4/4 tests passed
```

### Demo Script

Interactive demo in `demo_generator.py` shows Python shell usage:
```bash
$ python demo_generator.py
✅ All acceptance criteria demonstrated successfully!
```

## Included Template Modules

### webserver
- Install Apache or Nginx
- Configure port
- SSL support
- Service management with handlers

### database
- Install MySQL or PostgreSQL
- Create database and user
- Optional automated backups
- Service management

### user_management
- Create system users
- Add SSH keys
- Configure sudo access
- Group management

### firewall
- Install and configure UFW
- Set default policy
- Allow specific ports
- Loop over port list

## Documentation

### Comprehensive Documentation Created:
1. **`generator/README.md`** - Full API reference and usage guide
2. **`GENERATOR_ENGINE.md`** - This implementation summary
3. **Inline docstrings** - All classes and methods documented
4. **Code comments** - Complex logic explained

## Usage Examples

### Basic Usage

```python
from generator import PlaybookBuilder

builder = PlaybookBuilder()
builder.set_playbook_name("My Playbook")
builder.set_hosts("all")
builder.add_module('webserver', {
    'server_type': 'nginx',
    'port': 80
})
output_path = builder.write_to_file()
```

### Multiple Modules

```python
builder = PlaybookBuilder()
builder.set_playbook_name("Full Setup")
builder.add_module('webserver', {...})
builder.add_module('database', {...})
builder.add_module('firewall', {...})
builder.write_to_file('full_setup.yml')
```

### Custom Variables and Tasks

```python
builder = PlaybookBuilder()
builder.set_playbook_name("Custom Deployment")
builder.add_vars({'app_name': 'myapp', 'version': '1.0'})
builder.add_task({
    'name': 'Deploy {{ app_name }}',
    'debug': {'msg': 'Deploying version {{ version }}'}
})
builder.write_to_file(timestamped=True)
```

### Validation

```python
from generator import ValidationError

try:
    builder.add_module('database', {})  # Missing required params
except ValidationError as e:
    print(f"Error: {e}")
    # Error: Module 'database' missing required parameters: db_name, db_user.
    #        Please provide values for these fields.
```

## Key Features

1. **Type-safe data structures** with dataclasses
2. **Comprehensive validation** with actionable error messages
3. **Jinja2 integration** for flexible templating
4. **YAML-based template library** for easy module creation
5. **Method chaining** for fluent API
6. **Timestamped filenames** for versioning
7. **Automatic directory management** for output files
8. **Complete test coverage** with 78 passing tests
9. **Full documentation** with examples and API reference
10. **Backwards compatible** with existing playbook_generator package

## Conclusion

The generator engine has been successfully implemented with all ticket requirements met:

✅ Python modules under `generator/`  
✅ YAML template library with PyYAML  
✅ Validation for required fields  
✅ Data structures for modules, prompts, and tasks  
✅ Jinja2 rendering layer  
✅ Support for loop, when, notify  
✅ Task dictionaries ready for YAML serialization  
✅ PlaybookBuilder aggregating modules  
✅ Custom variables support  
✅ Writes to `generated_playbooks/`  
✅ Helper utilities for naming and directory management  
✅ Acceptance criteria verified  

The implementation is production-ready, well-tested, and fully documented.
