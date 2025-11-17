#!/usr/bin/env python3
"""Acceptance test for the generator engine.

This script demonstrates the acceptance criteria:
- Importing the builder in a Python shell
- Loading templates
- Rendering a module with sample data
- Combining multiple tasks into a playbook structure
- Writing a syntactically valid playbook file
"""

import os
import sys
import yaml

from generator import PlaybookBuilder, TemplateLibrary, ValidationError


def test_basic_workflow():
    """Test basic workflow: load, render, build, write."""
    print("=" * 60)
    print("Testing Generator Engine - Basic Workflow")
    print("=" * 60)
    
    print("\n1. Creating PlaybookBuilder instance...")
    builder = PlaybookBuilder()
    print("   ✓ Builder created successfully")
    
    print("\n2. Listing available modules...")
    modules = builder.list_modules()
    print(f"   Available modules: {', '.join(modules)}")
    print("   ✓ Templates loaded from library")
    
    if not modules:
        print("   ⚠ No modules found. Creating sample module...")
        return False
    
    print("\n3. Getting module information...")
    module_name = modules[0] if modules else None
    if module_name:
        module_info = builder.get_module_info(module_name)
        print(f"   Module: {module_info.name}")
        print(f"   Description: {module_info.description}")
        print(f"   Tasks: {len(module_info.tasks)}")
        print(f"   Handlers: {len(module_info.handlers)}")
        print("   ✓ Module info retrieved")
    
    print("\n4. Building a playbook with sample data...")
    builder.set_playbook_name("Test Web Server Playbook")
    builder.set_hosts("webservers")
    builder.add_vars({"environment": "production"})
    
    if 'webserver' in modules:
        sample_params = {
            'server_type': 'nginx',
            'port': 80,
            'enable_ssl': False
        }
        print(f"   Adding webserver module with params: {sample_params}")
        builder.add_module('webserver', sample_params)
        print("   ✓ Module added to playbook")
    
    print("\n5. Building playbook structure...")
    playbook_dict = builder.build()
    print(f"   Playbook name: {playbook_dict['name']}")
    print(f"   Target hosts: {playbook_dict['hosts']}")
    print(f"   Number of tasks: {len(playbook_dict['tasks'])}")
    print("   ✓ Playbook structure built")
    
    print("\n6. Converting to YAML...")
    yaml_content = builder.to_yaml()
    print("   First 300 characters of YAML:")
    print("   " + "\n   ".join(yaml_content[:300].split('\n')))
    print("   ✓ YAML generated")
    
    print("\n7. Validating YAML syntax...")
    try:
        parsed = yaml.safe_load(yaml_content)
        assert isinstance(parsed, list)
        assert len(parsed) > 0
        assert 'name' in parsed[0]
        assert 'tasks' in parsed[0]
        print("   ✓ YAML is syntactically valid")
    except Exception as e:
        print(f"   ✗ YAML validation failed: {e}")
        return False
    
    print("\n8. Writing to file...")
    output_path = builder.write_to_file(timestamped=True)
    print(f"   File written to: {output_path}")
    print(f"   File exists: {os.path.exists(output_path)}")
    print("   ✓ Playbook written to disk")
    
    print("\n9. Verifying file content...")
    with open(output_path, 'r') as f:
        file_content = f.read()
    file_parsed = yaml.safe_load(file_content)
    print(f"   File contains {len(file_parsed)} play(s)")
    print(f"   First play has {len(file_parsed[0].get('tasks', []))} task(s)")
    print("   ✓ File content verified")
    
    print("\n" + "=" * 60)
    print("✓ All acceptance criteria passed!")
    print("=" * 60)
    return True


def test_multiple_modules():
    """Test combining multiple modules into a single playbook."""
    print("\n" + "=" * 60)
    print("Testing Multiple Module Aggregation")
    print("=" * 60)
    
    builder = PlaybookBuilder()
    builder.set_playbook_name("Complete Server Setup")
    builder.set_hosts("all")
    
    modules = builder.list_modules()
    print(f"\nAvailable modules: {', '.join(modules)}")
    
    added_count = 0
    
    if 'webserver' in modules:
        print("\n1. Adding webserver module...")
        builder.add_module('webserver', {
            'server_type': 'apache2',
            'port': 8080,
            'enable_ssl': True
        })
        added_count += 1
        print("   ✓ Webserver module added")
    
    if 'firewall' in modules:
        print("\n2. Adding firewall module...")
        builder.add_module('firewall', {
            'allowed_ports': '22,8080,443',
            'default_policy': 'deny'
        })
        added_count += 1
        print("   ✓ Firewall module added")
    
    if 'user_management' in modules:
        print("\n3. Adding user_management module...")
        builder.add_module('user_management', {
            'username': 'deploy',
            'user_groups': 'sudo,www-data',
            'sudo_access': True
        })
        added_count += 1
        print("   ✓ User management module added")
    
    if added_count == 0:
        print("   ⚠ No modules available to add")
        return False
    
    print(f"\n4. Building playbook with {added_count} modules...")
    playbook = builder.build()
    print(f"   Total tasks: {len(playbook['tasks'])}")
    print(f"   Total handlers: {len(playbook.get('handlers', []))}")
    
    print("\n5. Writing combined playbook...")
    output_path = builder.write_to_file('combined_setup.yml')
    print(f"   Written to: {output_path}")
    
    print("\n" + "=" * 60)
    print("✓ Multiple module aggregation successful!")
    print("=" * 60)
    return True


def test_validation():
    """Test validation with missing required fields."""
    print("\n" + "=" * 60)
    print("Testing Validation")
    print("=" * 60)
    
    builder = PlaybookBuilder()
    
    print("\n1. Testing missing required parameters...")
    try:
        builder.set_playbook_name("Test")
        builder.set_hosts("all")
        builder.add_module('database', {})
        print("   ✗ Should have raised ValidationError")
        return False
    except ValidationError as e:
        print(f"   ✓ Validation error caught: {e}")
    
    print("\n2. Testing missing playbook name...")
    builder.reset()
    builder.set_hosts("all")
    try:
        builder.add_task({'name': 'Test task', 'debug': {'msg': 'test'}})
        builder.build()
        print("   ✗ Should have raised ValidationError")
        return False
    except ValidationError as e:
        print(f"   ✓ Validation error caught: {e}")
    
    print("\n3. Testing non-existent module...")
    builder.reset()
    builder.set_playbook_name("Test")
    try:
        builder.add_module('nonexistent_module', {})
        print("   ✗ Should have raised ValidationError")
        return False
    except ValidationError as e:
        print(f"   ✓ Validation error caught: {e}")
    
    print("\n" + "=" * 60)
    print("✓ Validation tests passed!")
    print("=" * 60)
    return True


def test_custom_variables():
    """Test adding custom variables to playbook."""
    print("\n" + "=" * 60)
    print("Testing Custom Variables")
    print("=" * 60)
    
    builder = PlaybookBuilder()
    builder.set_playbook_name("Custom Variables Test")
    builder.set_hosts("localhost")
    
    print("\n1. Adding custom variables...")
    custom_vars = {
        'app_name': 'myapp',
        'app_version': '1.2.3',
        'environment': 'staging',
        'debug_mode': True
    }
    builder.add_vars(custom_vars)
    print(f"   Added {len(custom_vars)} variables")
    
    print("\n2. Adding a custom task...")
    builder.add_task({
        'name': 'Deploy application',
        'debug': {
            'msg': 'Deploying {{ app_name }} version {{ app_version }}'
        }
    })
    
    print("\n3. Building playbook...")
    playbook = builder.build()
    print(f"   Variables in playbook: {list(playbook['vars'].keys())}")
    
    print("\n4. Writing playbook...")
    output_path = builder.write_to_file('custom_vars_test.yml')
    print(f"   Written to: {output_path}")
    
    with open(output_path, 'r') as f:
        content = f.read()
        print("\n   Playbook content:")
        for line in content.split('\n')[:20]:
            print(f"   {line}")
    
    print("\n" + "=" * 60)
    print("✓ Custom variables test passed!")
    print("=" * 60)
    return True


def main():
    """Run all acceptance tests."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Generator Engine Acceptance Tests" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")
    
    tests = [
        ("Basic Workflow", test_basic_workflow),
        ("Multiple Modules", test_multiple_modules),
        ("Validation", test_validation),
        ("Custom Variables", test_custom_variables),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All acceptance tests passed! 🎉")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
