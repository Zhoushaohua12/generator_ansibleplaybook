#!/usr/bin/env python3
"""
Integration test for the Ansible Module Templates Catalogue.

Demonstrates that the catalogue:
1. Loads successfully with PyYAML
2. Provides all required metadata for each module
3. Can be used to generate Ansible tasks with Jinja2
4. Supports all required modules from the ticket specification
"""

import yaml
from pathlib import Path
from jinja2 import Template


def test_catalogue_load():
    """Test that the catalogue loads successfully."""
    catalogue_path = Path('templates/ansible_modules.yaml')
    assert catalogue_path.exists(), "Catalogue file not found"
    
    with open(catalogue_path, 'r') as f:
        data = yaml.safe_load(f)
    
    assert data is not None, "Catalogue YAML is empty"
    assert 'modules' in data, "Catalogue missing 'modules' key"
    assert isinstance(data['modules'], list), "modules must be a list"
    
    print("✓ Catalogue loaded successfully")
    return data


def test_module_metadata():
    """Test that all modules have required metadata."""
    data = test_catalogue_load()
    modules = data['modules']
    
    required_fields = [
        'name', 'human_name', 'description', 'ansible_module',
        'default_task_name', 'category', 'prompts', 'handlers', 'task_template'
    ]
    
    for i, module in enumerate(modules, 1):
        for field in required_fields:
            assert field in module, f"Module #{i} missing '{field}'"
        
        assert isinstance(module['prompts'], list), \
            f"Module {module['name']}: prompts must be a list"
        assert isinstance(module['handlers'], list), \
            f"Module {module['name']}: handlers must be a list"
        assert isinstance(module['task_template'], str), \
            f"Module {module['name']}: task_template must be a string"
    
    print(f"✓ All {len(modules)} modules have required metadata")


def test_required_modules():
    """Test that all modules requested in the ticket are present."""
    data = test_catalogue_load()
    modules = data['modules']
    module_names = {m['name'] for m in modules}
    
    required_modules = {
        # System modules
        'user', 'group', 'service', 'package', 'yum', 'apt', 'systemd',
        # File modules
        'command', 'shell', 'file', 'copy', 'lineinfile', 'replace',
        'blockinfile', 'template', 'stat',
        # Network modules
        'firewalld', 'iptables',
        # Other modules
        'debug', 'set_fact', 'include_tasks', 'notify'
    }
    
    missing = required_modules - module_names
    assert not missing, f"Missing required modules: {missing}"
    
    print(f"✓ All {len(required_modules)} required modules present")


def test_module_categories():
    """Test that modules are properly categorized."""
    data = test_catalogue_load()
    modules = data['modules']
    
    valid_categories = {'system', 'file', 'network', 'other'}
    category_counts = {}
    
    for module in modules:
        cat = module.get('category')
        assert cat in valid_categories, \
            f"Module {module['name']} has invalid category '{cat}'"
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    assert len(category_counts) == 4, "Not all categories represented"
    print(f"✓ Modules properly categorized:")
    for cat in sorted(category_counts.keys()):
        print(f"  - {cat}: {category_counts[cat]} modules")


def test_prompt_types():
    """Test that prompt types are valid."""
    data = test_catalogue_load()
    modules = data['modules']
    
    valid_types = {'string', 'integer', 'boolean', 'list', 'dict'}
    
    for module in modules:
        for prompt in module.get('prompts', []):
            ptype = prompt.get('type', 'string')
            assert ptype in valid_types, \
                f"Module {module['name']}, prompt {prompt['name']}: " \
                f"invalid type '{ptype}'"
            
            # Check for name and description
            assert 'name' in prompt, \
                f"Module {module['name']}: prompt missing 'name'"
            assert 'description' in prompt, \
                f"Module {module['name']}: prompt missing 'description'"
    
    print("✓ All prompt types are valid")


def test_template_rendering():
    """Test that templates can be rendered with Jinja2."""
    data = test_catalogue_load()
    modules = data['modules']
    
    # Test a few representative modules
    test_cases = [
        {
            'module_name': 'user',
            'context': {
                'default_task_name': 'Create user deploy',
                'username': 'deploy',
                'uid': 1005,
                'groups': 'sudo,docker',
                'shell': '/bin/bash',
                'home': '/home/deploy',
                'createhome': True,
                'state': 'present'
            }
        },
        {
            'module_name': 'file',
            'context': {
                'default_task_name': 'Create config directory',
                'filepath': '/etc/myapp',
                'state': 'directory',
                'mode': '0755',
                'owner': 'root',
                'group': None
            }
        },
        {
            'module_name': 'service',
            'context': {
                'default_task_name': 'Start nginx service',
                'service_name': 'nginx',
                'state': 'started',
                'enabled': True
            }
        }
    ]
    
    for test_case in test_cases:
        module = next(m for m in modules if m['name'] == test_case['module_name'])
        template_str = module['task_template']
        template = Template(template_str)
        
        rendered = template.render(test_case['context'])
        
        assert rendered, f"Module {test_case['module_name']}: rendered output is empty"
        assert 'name:' in rendered, f"Module {test_case['module_name']}: missing 'name' in output"
        
        print(f"✓ {test_case['module_name']} template renders successfully")


def test_module_features():
    """Test that modules support advanced features."""
    data = test_catalogue_load()
    modules = data['modules']
    
    features = {
        'when_support': 0,
        'loop_support': 0,
        'notify_support': 0,
        'register_support': 0,
        'modules_with_handlers': 0
    }
    
    for module in modules:
        template = module.get('task_template', '')
        
        if 'when' in template or '{% if' in template:
            features['when_support'] += 1
        if 'loop' in template or '{% for' in template:
            features['loop_support'] += 1
        if 'notify' in template:
            features['notify_support'] += 1
        if 'register' in template:
            features['register_support'] += 1
        
        if module.get('handlers'):
            features['modules_with_handlers'] += 1
    
    print("✓ Advanced feature support:")
    print(f"  - {features['when_support']} modules support 'when' conditions")
    print(f"  - {features['loop_support']} modules support 'loop' iterations")
    print(f"  - {features['notify_support']} modules support 'notify' handlers")
    print(f"  - {features['register_support']} modules support 'register' variables")
    print(f"  - {features['modules_with_handlers']} modules define handlers")


def test_metadata_completeness():
    """Test that metadata is complete and useful."""
    data = test_catalogue_load()
    modules = data['modules']
    
    for module in modules:
        # Human name should be descriptive
        assert len(module['human_name']) > 5, \
            f"Module {module['name']}: human_name too short"
        
        # Description should explain purpose
        assert len(module['description']) > 10, \
            f"Module {module['name']}: description too short"
        
        # Task template should be substantial
        assert len(module['task_template']) > 20, \
            f"Module {module['name']}: task_template too short"
        
        # At least one prompt
        assert len(module['prompts']) > 0, \
            f"Module {module['name']}: no prompts defined"
    
    print("✓ All module metadata is complete and descriptive")


def test_module_naming_consistency():
    """Test that module names follow conventions."""
    data = test_catalogue_load()
    modules = data['modules']
    
    for module in modules:
        name = module['name']
        
        # Should be lowercase
        assert name.islower(), \
            f"Module name '{name}' should be lowercase"
        
        # Should use underscores for multi-word names
        if '_' in name:
            parts = name.split('_')
            for part in parts:
                assert part.isalpha(), \
                    f"Module name '{name}' contains invalid characters"
    
    print("✓ Module names follow naming conventions")


def main():
    """Run all integration tests."""
    print("=" * 70)
    print("ANSIBLE MODULE TEMPLATES CATALOGUE INTEGRATION TESTS")
    print("=" * 70)
    print()
    
    tests = [
        ("Catalogue Loading", test_catalogue_load),
        ("Module Metadata", test_module_metadata),
        ("Required Modules", test_required_modules),
        ("Module Categories", test_module_categories),
        ("Prompt Types", test_prompt_types),
        ("Template Rendering", test_template_rendering),
        ("Module Features", test_module_features),
        ("Metadata Completeness", test_metadata_completeness),
        ("Naming Consistency", test_module_naming_consistency),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\nTesting: {test_name}")
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    exit(main())
