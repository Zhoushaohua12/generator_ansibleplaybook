# Ansible Playbook Generator - CLI Workflow

This document describes the comprehensive CLI workflow implemented for generating Ansible playbooks from Jinja2 templates.

## Overview

The `ansible_playbook_generator.py` script provides both interactive and CLI-driven generation of Ansible playbooks. It supports menu-based interaction and command-line arguments for scripting scenarios.

## Features

### ✅ Implemented Features

1. **Main Entry Point**: `ansible_playbook_generator.py` with `if __name__ == "__main__"` support
2. **Menu-Based Interface**: Lists module categories and templates from the repository
3. **Multi-Module Selection**: Allows selecting multiple modules interactively
4. **Advanced Input Options**: Supports loops, when conditions, variables, and handlers
5. **Command-Line Arguments**: Complete CLI support for scripting scenarios
6. **Parameter Collection**: Iterative parameter input with validation
7. **Preview & Confirmation**: Shows playbook preview before saving
8. **Generated Playbooks Directory**: Saves all playbooks under `generated_playbooks/`

## Usage

### Interactive Mode

Launch the script without arguments to start interactive mode:

```bash
python ansible_playbook_generator.py
```

This will display a menu with available module categories:
```
==================================================
Ansible Playbook Generator
==================================================

Available Module Categories:

1. Basic
   1.1 basic

2. Conditional
   2.1 conditional

3. Multi-task
   3.1 with_tasks

Select option (e.g., 1, 1.1):
```

### Non-Interactive Mode

Use command-line arguments for scripting:

```bash
# Generate a basic playbook
python ansible_playbook_generator.py --modules basic --output my_playbook.yml

# Generate multiple playbooks
python ansible_playbook_generator.py --modules basic,conditional --output multi.yml

# Use variables file
python ansible_playbook_generator.py --modules with_tasks --vars-file vars.yml --inventory production

# Complete example
python ansible_playbook_generator.py \
  --modules basic,conditional,with_tasks \
  --vars-file production_vars.yml \
  --inventory production \
  --playbook-name "Production Setup" \
  --output production_setup.yml
```

## Command-Line Arguments

| Argument | Short | Description | Example |
|----------|-------|-------------|---------|
| `--modules` | `-m` | Comma-separated list of modules to use | `basic,conditional` |
| `--output` | `-o` | Output file path | `my_playbook.yml` |
| `--inventory` | `-i` | Target inventory/hosts | `production` |
| `--vars-file` | `-v` | Path to YAML variables file | `vars.yml` |
| `--playbook-name` | `-n` | Name for the generated playbook | `My Playbook` |
| `--interactive` | `--int` | Force interactive mode | - |

## Template Categories

### Basic Templates
- **basic**: Simple playbook with basic structure and debug task

### Conditional Templates  
- **conditional**: Supports variables, conditions, and when clauses

### Multi-Task Templates
- **with_tasks**: Supports multiple tasks with different modules

## Variables File Format

Create a YAML file with your variables:

```yaml
# production_vars.yml
playbook_name: "Production Setup"
hosts: "production_servers"
vars:
  environment: "production"
  debug_mode: false
  app_version: "1.2.3"
tasks:
  - name: "Install application"
    module: "apt"
    params:
      name: "myapp"
      state: "present"
    when: "environment == 'production'"
```

## Generated Playbook Examples

### Basic Playbook
```yaml
---
- name: My Playbook
  hosts: all
  gather_facts: yes
  tasks:
    - name: Debug message
      debug:
        msg: "Running My Playbook"
```

### Multi-Task Playbook
```yaml
---
- name: Multi-Task Playbook
  hosts: web_servers
  gather_facts: yes
  tasks:
    - name: Install Nginx
      apt:
        name: nginx
        state: present
    
    - name: Start Nginx
      service:
        name: nginx
        state: started
```

### Conditional Playbook
```yaml
---
- name: Conditional Playbook
  hosts: production
  gather_facts: yes
  
  vars:
    environment: production
    debug_mode: false
  
  tasks:
    - name: Configure production
      template:
        src: config.j2
        dest: /etc/app/config
      when: environment == 'production'
```

## Working Directory Structure

```
project/
├── ansible_playbook_generator.py    # Main entry point
├── playbook_generator/              # Package directory
│   ├── cli.py                      # Original CLI (still available)
│   ├── template_loader.py          # Template loading utilities
│   ├── renderer.py                 # Jinja2 rendering
│   ├── playbook_builder.py         # Playbook building
│   └── templates/                  # Jinja2 templates
│       ├── basic.j2
│       ├── conditional.j2
│       └── with_tasks.j2
├── generated_playbooks/            # Output directory
│   ├── basic_playbook.yml
│   ├── conditional_playbook.yml
│   └── with_tasks_playbook.yml
└── vars.yml                        # Example variables file
```

## Advanced Features

### Interactive Parameter Collection

The interactive mode guides you through collecting parameters for each template:

1. **Basic Parameters**: Playbook name, target hosts
2. **Task Configuration**: Module selection, parameters, conditions
3. **Variable Input**: Custom variables with YAML parsing
4. **Loop Configuration**: Loop types and control options
5. **Handler Support**: Event-driven task execution

### Validation and Error Handling

- Template existence validation
- YAML syntax checking for variables
- Parameter type validation
- Graceful error handling with user feedback

### Output Management

- Automatic directory creation (`generated_playbooks/`)
- Unique filename generation for multiple modules
- Absolute path resolution
- Overwrite protection with user confirmation

## Testing

The implementation includes comprehensive testing:

```bash
# Run acceptance tests
python test_acceptance.py

# Run comprehensive feature tests  
python test_comprehensive.py

# Run interactive workflow demo
python demo_workflow.py
```

## Integration with Existing CLI

The new `ansible_playbook_generator.py` complements the existing `playbook-gen` command:

- `playbook-gen`: Original CLI for basic operations
- `ansible_playbook_generator.py`: Full-featured workflow with advanced options

Both use the same underlying components (`TemplateLoader`, `PlaybookBuilder`, `Renderer`) ensuring consistency.

## Acceptance Criteria Met

✅ **Main Entry Point**: Implemented `ansible_playbook_generator.py` with proper `if __name__ == "__main__"`  
✅ **Menu-Based Interface**: Lists categories and modules from template repository  
✅ **Multi-Module Selection**: Supports selecting multiple modules iteratively  
✅ **Advanced Input Options**: Loops, conditions, variables, handlers supported  
✅ **Command-Line Arguments**: Complete CLI support for scripting scenarios  
✅ **Parameter Collection**: Iterative input collection with validation  
✅ **Preview & Save**: Summary preview and save location confirmation  
✅ **Generated Playbooks Directory**: All playbooks saved under `generated_playbooks/`  
✅ **Interactive Mode**: Full interactive workflow working  
✅ **Non-Interactive Mode**: Scripting scenarios fully supported  

The CLI workflow is now complete and ready for use!