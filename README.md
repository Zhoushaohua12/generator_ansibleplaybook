# Playbook Generator

A Python CLI tool for generating Ansible playbooks from Jinja2 templates. The tool provides an intuitive way to create playbooks with consistent structure, support for complex task definitions, conditional logic, and loops.

## Features

- 🎯 **Template-based generation**: Use pre-defined templates to generate Ansible playbooks
- 🔄 **Interactive mode**: Menu-driven interface for generating playbooks
- 📝 **YAML parameters**: Define playbook parameters in YAML files
- 🔗 **Template loops and conditions**: Support for Jinja2 loops and when clauses
- 🧪 **Comprehensive test suite**: Full pytest coverage with fixtures and CLI tests
- 📚 **Multiple templates**: Basic, task-based, and conditional playbook templates included
- 🏗️ **Generator Engine**: Python API for programmatic playbook generation from YAML module library

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Interactive Mode](#interactive-mode)
  - [Command-line Mode](#command-line-mode)
  - [Using Parameter Files](#using-parameter-files)
- [Generator Engine](#generator-engine)
- [Templates](#templates)
  - [Basic Template](#basic-template)
  - [Task Template](#task-template)
  - [Conditional Template](#conditional-template)
- [Adding New Templates](#adding-new-templates)
- [Running Tests](#running-tests)
- [Example Output](#example-output)
- [Development](#development)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd playbook-generator
```

### Step 2: Install Dependencies

Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

### Verify Installation

Check that the installation was successful:

```bash
playbook-gen --help
```

You should see help output for the available commands.

## Quick Start

### List Available Templates

See all available templates:

```bash
playbook-gen list-templates
```

Example output:
```
Available templates:
  - basic
  - conditional
  - with_tasks
```

### Generate a Playbook (Interactive Mode)

Run the generator in interactive mode:

```bash
playbook-gen generate
```

The tool will:
1. Display available templates
2. Ask you to select a template
3. Prompt for basic playbook parameters
4. Generate the playbook and save to `playbook.yml`

Example session:
```
Available templates:
  1. basic
  2. conditional
  3. with_tasks

Select a template: 1
Playbook name [My Playbook]: Web Server Deploy
Target hosts [all]: webservers
✓ Playbook generated: /path/to/playbook.yml
```

### Generate from Command Line

Generate a playbook using command-line arguments:

```bash
playbook-gen generate basic -o my_playbook.yml
```

Then provide the parameters when prompted:
```
Playbook name [My Playbook]: Deploy Web App
Target hosts [all]: production
✓ Playbook generated: /path/to/my_playbook.yml
```

## Usage

### Interactive Mode

Use the interactive generator for step-by-step playbook creation:

```bash
playbook-gen generate
```

The interactive mode guides you through:
- Template selection from available options
- Parameter input with sensible defaults
- File output specification

### Command-line Mode

Specify template and output path directly:

```bash
playbook-gen generate TEMPLATE_NAME -o output.yml
```

**Options:**
- `TEMPLATE_NAME`: Name of the template to use (optional for interactive mode)
- `-o, --output`: Output file path (default: `playbook.yml`)

### Using Parameter Files

For complex playbooks with many parameters, use YAML parameter files:

```bash
playbook-gen generate-from-file TEMPLATE_NAME parameters.yaml -o output.yml
```

**Arguments:**
- `TEMPLATE_NAME`: Name of the template to use
- `PARAMETERS`: Path to YAML file containing parameters
- `-o, --output`: Output file path (default: `playbook.yml`)

#### Example Parameter File

Create `webserver_params.yaml`:

```yaml
playbook_name: "Deploy Web Servers"
hosts: "web_group"
vars:
  environment: "production"
  enable_ssl: true

tasks:
  - name: "Install Apache"
    module: "package"
    params:
      name: "apache2"
      state: "present"
  
  - name: "Start Apache"
    module: "service"
    params:
      name: "apache2"
      state: "started"
      enabled: "yes"
    when: "enable_ssl"
```

Then generate the playbook:

```bash
playbook-gen generate-from-file with_tasks webserver_params.yaml -o webservers.yml
```

## Generator Engine

The generator engine provides a Python API for programmatic playbook generation from YAML module templates.

### Quick Start with Generator Engine

```python
from generator import PlaybookBuilder

# Create builder and list available modules
builder = PlaybookBuilder()
modules = builder.list_modules()
print(f"Available modules: {modules}")

# Build a playbook with multiple modules
builder.set_playbook_name("Production Server Setup")
builder.set_hosts("production")

# Add webserver module
builder.add_module('webserver', {
    'server_type': 'nginx',
    'port': 80,
    'enable_ssl': False
})

# Add firewall module
builder.add_module('firewall', {
    'allowed_ports': '22,80,443',
    'default_policy': 'deny'
})

# Write to generated_playbooks/ directory
output_path = builder.write_to_file()
print(f"Playbook written to: {output_path}")
```

### Features

- **YAML Module Library**: Define reusable modules in `generator/template_library/`
- **Validation**: Comprehensive validation with actionable error messages
- **Jinja2 Rendering**: Full Jinja2 template support in module definitions
- **Optional Sections**: Support for `loop`, `when`, `notify` in tasks
- **Multiple Modules**: Combine multiple modules into a single playbook
- **Custom Variables**: Add custom variables to playbooks
- **Timestamped Files**: Optional timestamped output filenames

### Included Modules

- **webserver**: Install and configure Apache or Nginx
- **database**: Set up MySQL or PostgreSQL with users and backups
- **user_management**: Create system users with SSH keys and sudo access
- **firewall**: Configure UFW firewall with custom rules

### Documentation

For complete API reference and usage examples, see:
- `generator/README.md` - Full generator engine documentation
- `GENERATOR_ENGINE.md` - Implementation details and architecture
- `demo_generator.py` - Interactive demo script

### Demo

Run the demo to see the generator engine in action:

```bash
python demo_generator.py
```

Run acceptance tests:

```bash
python test_generator_acceptance.py
```

## Templates

### Basic Template

The simplest template for creating straightforward playbooks.

**Use case:** Simple host configuration, basic information gathering

**Parameters:**
- `playbook_name` (string): Name of the playbook
- `hosts` (string): Target hosts pattern

**Example:**

```bash
playbook-gen generate basic -o basic.yml
```

**Generated playbook structure:**

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

### Task Template

Template for playbooks with multiple tasks including loops.

**Use case:** Multi-step deployments, service configuration, package installation

**Parameters:**
- `playbook_name` (string): Name of the playbook
- `hosts` (string): Target hosts pattern
- `tasks` (array): List of tasks to execute

**Task Structure:**
```yaml
tasks:
  - name: "Task name"
    module: "ansible_module_name"
    params:
      key1: "value1"
      key2: "value2"
```

**Example parameter file:**

```yaml
playbook_name: "Install Services"
hosts: "all"
tasks:
  - name: "Install nginx"
    module: "package"
    params:
      name: "nginx"
      state: "present"
  
  - name: "Start nginx"
    module: "service"
    params:
      name: "nginx"
      state: "started"
```

**Generated playbook snippet:**

```yaml
---
- name: Install Services
  hosts: all
  gather_facts: yes
  tasks:
    - name: Install nginx
      package:
        name: nginx
        state: present
    
    - name: Start nginx
      service:
        name: nginx
        state: started
```

### Conditional Template

Template for playbooks with conditional task execution using `when` clauses.

**Use case:** Environment-specific deployments, feature toggles, platform-specific tasks

**Parameters:**
- `playbook_name` (string): Name of the playbook
- `hosts` (string): Target hosts pattern
- `vars` (object): Variables available to conditionals
- `tasks` (array): List of tasks with optional `when` conditions

**Task Structure with Conditionals:**
```yaml
tasks:
  - name: "Task name"
    module: "ansible_module_name"
    params:
      key: "value"
    when: "condition"
```

**Example parameter file:**

```yaml
playbook_name: "Production Deployment"
hosts: "production"
vars:
  environment: "production"
  enable_monitoring: true

tasks:
  - name: "Install monitoring tools"
    module: "package"
    params:
      name: "prometheus"
      state: "present"
    when: "enable_monitoring"
  
  - name: "Configure alerts"
    module: "template"
    params:
      src: "alerts.j2"
      dest: "/etc/monitoring/alerts.conf"
    when: "environment == 'production'"
```

**Generated playbook snippet:**

```yaml
---
- name: Production Deployment
  hosts: production
  gather_facts: yes
  vars:
    environment: production
    enable_monitoring: true
  tasks:
    - name: Install monitoring tools
      package:
        name: prometheus
        state: present
      when: enable_monitoring
    
    - name: Configure alerts
      template:
        src: alerts.j2
        dest: /etc/monitoring/alerts.conf
      when: environment == 'production'
```

## Adding New Templates

Extend the tool with custom templates for your specific use cases.

### Step 1: Create a Template File

Create a new Jinja2 template in the `playbook_generator/templates/` directory with a `.j2` extension.

**Example:** `custom_template.j2`

```jinja2
---
- name: {{ playbook_name | default('Custom Playbook') }}
  hosts: {{ hosts | default('all') }}
  gather_facts: {{ gather_facts | default(true) }}
  {% if handlers %}
  handlers:
    {% for handler in handlers %}
    - name: {{ handler.name }}
      {{ handler.module }}:
        {% for key, value in handler.params.items() %}
        {{ key }}: {{ value }}
        {% endfor %}
    {% endfor %}
  {% endif %}
  tasks:
    {% for task in tasks | default([]) %}
    - name: {{ task.name }}
      {{ task.module }}:
        {% for key, value in task.params | default({}).items() %}
        {{ key }}: {{ value }}
        {% endfor %}
      {% if task.register %}
      register: {{ task.register }}
      {% endif %}
      {% if task.notify %}
      notify:
        {% for notification in task.notify %}
        - {{ notification }}
        {% endfor %}
      {% endif %}
    {% endfor %}
```

### Step 2: Create a Schema File (Optional)

Create a schema file to document template parameters:

**Example:** `custom_template_schema.yaml`

```yaml
description: "Custom template for advanced playbooks"
parameters:
  playbook_name:
    type: string
    description: "Name of the playbook"
    required: true
  hosts:
    type: string
    description: "Target hosts pattern"
    required: true
  handlers:
    type: array
    description: "List of handlers"
    required: false
  tasks:
    type: array
    description: "List of tasks"
    required: true
```

### Step 3: Verify the Template

List templates to see your new template:

```bash
playbook-gen list-templates
```

Generate a playbook using your new template:

```bash
playbook-gen generate custom-template -o output.yml
```

## Running Tests

The project includes comprehensive pytest tests covering template loading, rendering, playbook building, and CLI functionality.

### Run All Tests

```bash
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest tests/test_template_loader.py
```

### Run Specific Test Class

```bash
pytest tests/test_template_loader.py::TestTemplateLoader
```

### Run Specific Test

```bash
pytest tests/test_cli.py::TestCLI::test_list_templates_command
```

### Run with Coverage Report

```bash
pytest --cov=playbook_generator
```

### Run with Coverage Report (HTML)

```bash
pytest --cov=playbook_generator --cov-report=html
```

### Test Organization

Tests are organized by functionality:

- **test_template_loader.py**: Tests for template discovery, loading, and validation
- **test_renderer.py**: Tests for template rendering with parameters, loops, and conditionals
- **test_playbook_builder.py**: Tests for playbook assembly and file writing
- **test_cli.py**: Tests for CLI commands, interactive mode simulation, and file generation

### Test Fixtures

Fixture data is provided in `tests/fixtures/` for realistic test scenarios:

- **basic_params.yaml**: Parameters for basic template tests
- **with_tasks_params.yaml**: Complex parameters with multiple tasks
- **conditional_params.yaml**: Parameters with conditional logic

## Example Output

### Example 1: Basic Playbook

**Command:**
```bash
playbook-gen generate basic -o basic_playbook.yml
```

**Output file (basic_playbook.yml):**
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

### Example 2: Multi-task Playbook

**Parameter file (deploy.yaml):**
```yaml
playbook_name: "Deploy Application"
hosts: "app_servers"
tasks:
  - name: "Install dependencies"
    module: "package"
    params:
      name: "python3-pip"
      state: "present"
  
  - name: "Clone repository"
    module: "git"
    params:
      repo: "https://github.com/example/app.git"
      dest: "/opt/app"
  
  - name: "Install Python requirements"
    module: "pip"
    params:
      requirements: "/opt/app/requirements.txt"
```

**Command:**
```bash
playbook-gen generate-from-file with_tasks deploy.yaml -o deploy_playbook.yml
```

**Generated playbook (deploy_playbook.yml):**
```yaml
---
- name: Deploy Application
  hosts: app_servers
  gather_facts: yes
  tasks:
    - name: Install dependencies
      package:
        name: python3-pip
        state: present
    
    - name: Clone repository
      git:
        repo: https://github.com/example/app.git
        dest: /opt/app
    
    - name: Install Python requirements
      pip:
        requirements: /opt/app/requirements.txt
```

### Example 3: Conditional Playbook

**Parameter file (prod_deploy.yaml):**
```yaml
playbook_name: "Production Deployment"
hosts: "production"
vars:
  is_production: true
  enable_monitoring: true

tasks:
  - name: "Enable SELinux"
    module: "selinux"
    params:
      policy: "targeted"
      state: "enforcing"
    when: "is_production"
  
  - name: "Configure Prometheus"
    module: "template"
    params:
      src: "prometheus.yml.j2"
      dest: "/etc/prometheus/prometheus.yml"
    when: "enable_monitoring"
  
  - name: "Restart Prometheus"
    module: "service"
    params:
      name: "prometheus"
      state: "restarted"
    when: "enable_monitoring"
```

**Generated playbook:**
```yaml
---
- name: Production Deployment
  hosts: production
  gather_facts: yes
  vars:
    is_production: true
    enable_monitoring: true
  tasks:
    - name: Enable SELinux
      selinux:
        policy: targeted
        state: enforcing
      when: is_production
    
    - name: Configure Prometheus
      template:
        src: prometheus.yml.j2
        dest: /etc/prometheus/prometheus.yml
      when: enable_monitoring
    
    - name: Restart Prometheus
      service:
        name: prometheus
        state: restarted
      when: enable_monitoring
```

## Development

### Project Structure

```
playbook-generator/
├── playbook_generator/
│   ├── __init__.py
│   ├── cli.py                    # CLI commands
│   ├── template_loader.py        # Template loading and validation
│   ├── renderer.py               # Jinja2 template rendering
│   ├── playbook_builder.py       # Playbook building and writing
│   └── templates/
│       ├── basic.j2              # Basic template
│       ├── with_tasks.j2         # Multi-task template
│       └── conditional.j2        # Conditional template
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # pytest configuration and fixtures
│   ├── fixtures/                 # Test parameter files
│   │   ├── basic_params.yaml
│   │   ├── with_tasks_params.yaml
│   │   └── conditional_params.yaml
│   ├── test_template_loader.py   # Tests for template loading
│   ├── test_renderer.py          # Tests for rendering
│   ├── test_playbook_builder.py  # Tests for building
│   └── test_cli.py               # Tests for CLI
├── setup.py                      # Package setup
├── requirements.txt              # Dependencies
├── pytest.ini                    # pytest configuration
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

### Running in Development Mode

Install the package in editable mode:

```bash
pip install -e .
```

Now you can modify the source code and test immediately without reinstalling.

### Code Style

The project follows PEP 8 style guidelines. Format your code with:

```bash
pip install black
black playbook_generator tests
```

### Type Checking (Optional)

Install mypy for type checking:

```bash
pip install mypy
mypy playbook_generator
```

### Troubleshooting

**Issue:** `playbook-gen` command not found after installation

**Solution:** Ensure you've installed the package:
```bash
pip install -e .
```

Then verify:
```bash
which playbook-gen
playbook-gen --help
```

**Issue:** Template not found error

**Solution:** Ensure templates are in the correct directory:
```bash
ls playbook_generator/templates/
```

Should show `.j2` files for your templates.

**Issue:** Import errors when running tests

**Solution:** Ensure test dependencies are installed:
```bash
pip install -r requirements.txt
```

## Contributing

To contribute improvements:

1. Create a feature branch
2. Make your changes
3. Run tests: `pytest`
4. Submit a pull request

## License

[Add appropriate license here]

## Support

For issues, questions, or suggestions, please open an issue in the repository.
