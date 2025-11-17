#!/usr/bin/env python3
"""
Demo script showing the generator engine usage in a Python shell.

This demonstrates the acceptance criteria:
- Importing the builder in a Python shell
- Loading templates
- Rendering a module with sample data  
- Combining multiple tasks into a playbook structure
- Writing a syntactically valid playbook file
"""

print("=" * 70)
print("Generator Engine Demo - Python Shell Usage")
print("=" * 70)

print("\n# Step 1: Import the builder")
print(">>> from generator import PlaybookBuilder\n")
from generator import PlaybookBuilder

print("# Step 2: Create a builder instance")
print(">>> builder = PlaybookBuilder()\n")
builder = PlaybookBuilder()

print("# Step 3: Load and list available templates")
print(">>> modules = builder.list_modules()")
modules = builder.list_modules()
print(f">>> print(modules)")
print(modules)
print()

print("# Step 4: Get information about a module")
print(">>> webserver = builder.get_module_info('webserver')")
webserver = builder.get_module_info('webserver')
print(f">>> print(f'Module: {{webserver.name}}')")
print(f"Module: {webserver.name}")
print(f">>> print(f'Description: {{webserver.description}}')")
print(f"Description: {webserver.description}")
print(f">>> print(f'Tasks: {{len(webserver.tasks)}}')")
print(f"Tasks: {len(webserver.tasks)}")
print()

print("# Step 5: Render a module with sample data")
print(">>> builder.set_playbook_name('Demo Webserver Playbook')")
builder.set_playbook_name('Demo Webserver Playbook')
print(">>> builder.set_hosts('webservers')")
builder.set_hosts('webservers')
print(">>> builder.add_module('webserver', {")
print("...     'server_type': 'nginx',")
print("...     'port': 80,")
print("...     'enable_ssl': False")
print("... })")
builder.add_module('webserver', {
    'server_type': 'nginx',
    'port': 80,
    'enable_ssl': False
})
print()

print("# Step 6: Add custom variables")
print(">>> builder.add_vars({'environment': 'production'})")
builder.add_vars({'environment': 'production'})
print()

print("# Step 7: Combine multiple modules into a playbook")
print(">>> builder.add_module('firewall', {")
print("...     'allowed_ports': '22,80,443',")
print("...     'default_policy': 'deny'")
print("... })")
builder.add_module('firewall', {
    'allowed_ports': '22,80,443',
    'default_policy': 'deny'
})
print()

print("# Step 8: Build the playbook structure")
print(">>> playbook = builder.build()")
playbook = builder.build()
print(f">>> print(f'Playbook: {{playbook[\"name\"]}}')")
print(f"Playbook: {playbook['name']}")
print(f">>> print(f'Hosts: {{playbook[\"hosts\"]}}')")
print(f"Hosts: {playbook['hosts']}")
print(f">>> print(f'Tasks: {{len(playbook[\"tasks\"])}}')")
print(f"Tasks: {len(playbook['tasks'])}")
print(f">>> print(f'Handlers: {{len(playbook[\"handlers\"])}}')")
print(f"Handlers: {len(playbook['handlers'])}")
print()

print("# Step 9: Convert to YAML")
print(">>> yaml_content = builder.to_yaml()")
yaml_content = builder.to_yaml()
print(">>> print(yaml_content[:400])")
print(yaml_content[:400])
print("...\n")

print("# Step 10: Write syntactically valid playbook to disk")
print(">>> output_path = builder.write_to_file('demo_playbook.yml')")
output_path = builder.write_to_file('demo_playbook.yml')
print(f">>> print(f'Written to: {{output_path}}')")
print(f"Written to: {output_path}")
print()

print("# Step 11: Verify the file exists")
print(">>> import os")
import os
print(">>> os.path.exists(output_path)")
print(os.path.exists(output_path))
print()

print("# Step 12: Read and validate the generated YAML")
print(">>> import yaml")
import yaml
print(">>> with open(output_path, 'r') as f:")
print("...     content = yaml.safe_load(f)")
with open(output_path, 'r') as f:
    content = yaml.safe_load(f)
print(">>> print(f'Valid YAML: {isinstance(content, list)}')")
print(f"Valid YAML: {isinstance(content, list)}")
print(">>> print(f'Plays: {len(content)}')")
print(f"Plays: {len(content)}")
print(">>> print(f'First play name: {content[0][\"name\"]}')")
print(f"First play name: {content[0]['name']}")
print()

print("=" * 70)
print("✅ All acceptance criteria demonstrated successfully!")
print("=" * 70)
print("\nGenerated playbook location:")
print(f"  {output_path}")
print("\nTry it yourself:")
print("  python3")
print("  >>> from generator import PlaybookBuilder")
print("  >>> builder = PlaybookBuilder()")
print("  >>> builder.list_modules()")
