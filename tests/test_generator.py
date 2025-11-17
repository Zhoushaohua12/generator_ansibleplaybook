"""Tests for the generator engine module."""

import os
import pytest
import yaml
from generator import (
    PlaybookBuilder,
    TemplateLibrary,
    TemplateRenderer,
    ValidationError,
    Module,
    TaskTemplate,
    Prompt
)
from generator.utils import generate_filename, ensure_output_dir, sanitize_filename


class TestModels:
    """Test data model classes."""
    
    def test_prompt_validation(self):
        """Test prompt validation."""
        prompt = Prompt(
            name="test_param",
            description="Test parameter",
            type="string"
        )
        prompt.validate()
    
    def test_prompt_validation_missing_name(self):
        """Test prompt validation fails with missing name."""
        prompt = Prompt(name="", description="Test")
        with pytest.raises(ValidationError, match="must have a name"):
            prompt.validate()
    
    def test_prompt_validation_invalid_type(self):
        """Test prompt validation fails with invalid type."""
        prompt = Prompt(name="test", description="Test", type="invalid")
        with pytest.raises(ValidationError, match="invalid type"):
            prompt.validate()
    
    def test_task_template_validation(self):
        """Test task template validation."""
        task = TaskTemplate(
            name="Test task",
            module="debug",
            params={"msg": "test"}
        )
        task.validate()
    
    def test_task_template_to_dict(self):
        """Test task template to_dict conversion."""
        task = TaskTemplate(
            name="Test task",
            module="debug",
            params={"msg": "test"},
            when="test_var",
            notify=["handler1"]
        )
        result = task.to_dict()
        assert result['name'] == "Test task"
        assert result['debug'] == {"msg": "test"}
        assert result['when'] == "test_var"
        assert result['notify'] == ["handler1"]
    
    def test_module_validation(self):
        """Test module validation."""
        task = TaskTemplate(name="Test", module="debug", params={})
        module = Module(
            name="test_module",
            description="Test module",
            tasks=[task]
        )
        module.validate()
    
    def test_module_validation_missing_tasks(self):
        """Test module validation fails without tasks."""
        module = Module(
            name="test_module",
            description="Test module",
            tasks=[]
        )
        with pytest.raises(ValidationError, match="must have at least one task"):
            module.validate()


class TestTemplateLibrary:
    """Test template library loading."""
    
    def test_library_initialization(self):
        """Test library initializes successfully."""
        library = TemplateLibrary()
        assert library is not None
    
    def test_list_modules(self):
        """Test listing modules from library."""
        library = TemplateLibrary()
        modules = library.list_modules()
        assert isinstance(modules, list)
        assert len(modules) > 0
        assert 'webserver' in modules
    
    def test_get_module(self):
        """Test getting a specific module."""
        library = TemplateLibrary()
        module = library.get_module('webserver')
        assert module.name == 'webserver'
        assert module.description
        assert len(module.tasks) > 0
    
    def test_get_nonexistent_module_raises_error(self):
        """Test getting nonexistent module raises error."""
        library = TemplateLibrary()
        with pytest.raises(ValidationError, match="not found"):
            library.get_module('nonexistent')
    
    def test_validate_required_fields(self):
        """Test validation of required fields."""
        library = TemplateLibrary()
        library.validate_required_fields('webserver', {
            'server_type': 'nginx',
            'port': 80
        })
    
    def test_validate_required_fields_missing(self):
        """Test validation fails with missing required fields."""
        library = TemplateLibrary()
        with pytest.raises(ValidationError, match="missing required parameters"):
            library.validate_required_fields('database', {})


class TestTemplateRenderer:
    """Test template rendering."""
    
    def test_render_value_simple(self):
        """Test rendering simple template value."""
        renderer = TemplateRenderer()
        result = renderer.render_value("{{ var }}", {"var": "value"})
        assert result == "value"
    
    def test_render_value_no_template(self):
        """Test rendering non-template value."""
        renderer = TemplateRenderer()
        result = renderer.render_value("plain text", {})
        assert result == "plain text"
    
    def test_render_dict(self):
        """Test rendering dictionary."""
        renderer = TemplateRenderer()
        data = {
            "key1": "{{ var1 }}",
            "key2": "plain",
            "key3": "{{ var2 }}"
        }
        result = renderer.render_dict(data, {"var1": "value1", "var2": "value2"})
        assert result["key1"] == "value1"
        assert result["key2"] == "plain"
        assert result["key3"] == "value2"
    
    def test_render_task(self):
        """Test rendering task template."""
        renderer = TemplateRenderer()
        task = TaskTemplate(
            name="Install {{ package }}",
            module="package",
            params={"name": "{{ package }}", "state": "present"}
        )
        result = renderer.render_task(task, {"package": "nginx"})
        assert result['name'] == "Install nginx"
        assert result['package']['name'] == "nginx"
        assert result['package']['state'] == "present"
    
    def test_render_module(self):
        """Test rendering complete module."""
        renderer = TemplateRenderer()
        task = TaskTemplate(
            name="Test {{ param }}",
            module="debug",
            params={"msg": "{{ param }}"}
        )
        prompt = Prompt(name="param", description="Test", required=True)
        module = Module(
            name="test",
            description="Test",
            prompts=[prompt],
            tasks=[task]
        )
        
        result = renderer.render_module(module, {"param": "value"})
        assert len(result['tasks']) == 1
        assert result['tasks'][0]['name'] == "Test value"


class TestPlaybookBuilder:
    """Test playbook builder."""
    
    def test_builder_initialization(self):
        """Test builder initializes successfully."""
        builder = PlaybookBuilder()
        assert builder is not None
    
    def test_set_playbook_name(self):
        """Test setting playbook name."""
        builder = PlaybookBuilder()
        builder.set_playbook_name("Test Playbook")
        assert builder._playbook_data['name'] == "Test Playbook"
    
    def test_set_hosts(self):
        """Test setting hosts."""
        builder = PlaybookBuilder()
        builder.set_hosts("webservers")
        assert builder._playbook_data['hosts'] == "webservers"
    
    def test_add_vars(self):
        """Test adding variables."""
        builder = PlaybookBuilder()
        builder.add_vars({"var1": "value1", "var2": "value2"})
        assert builder._playbook_data['vars']['var1'] == "value1"
        assert builder._playbook_data['vars']['var2'] == "value2"
    
    def test_add_module(self):
        """Test adding a module."""
        builder = PlaybookBuilder()
        builder.set_playbook_name("Test")
        builder.add_module('webserver', {
            'server_type': 'nginx',
            'port': 80
        })
        assert len(builder._playbook_data['tasks']) > 0
    
    def test_add_task(self):
        """Test adding custom task."""
        builder = PlaybookBuilder()
        builder.set_playbook_name("Test")
        builder.add_task({"name": "Test", "debug": {"msg": "test"}})
        assert len(builder._playbook_data['tasks']) == 1
    
    def test_build_without_name_raises_error(self):
        """Test building without name raises error."""
        builder = PlaybookBuilder()
        builder.add_task({"name": "Test", "debug": {"msg": "test"}})
        with pytest.raises(ValidationError, match="must have a name"):
            builder.build()
    
    def test_build_without_tasks_raises_error(self):
        """Test building without tasks raises error."""
        builder = PlaybookBuilder()
        builder.set_playbook_name("Test")
        with pytest.raises(ValidationError, match="must have at least one task"):
            builder.build()
    
    def test_build_success(self):
        """Test successful build."""
        builder = PlaybookBuilder()
        builder.set_playbook_name("Test Playbook")
        builder.set_hosts("all")
        builder.add_task({"name": "Test", "debug": {"msg": "test"}})
        
        playbook = builder.build()
        assert playbook['name'] == "Test Playbook"
        assert playbook['hosts'] == "all"
        assert len(playbook['tasks']) == 1
    
    def test_to_yaml(self):
        """Test YAML conversion."""
        builder = PlaybookBuilder()
        builder.set_playbook_name("Test")
        builder.add_task({"name": "Test", "debug": {"msg": "test"}})
        
        yaml_content = builder.to_yaml()
        assert yaml_content.startswith('---')
        assert 'Test' in yaml_content
    
    def test_write_to_file(self, tmp_path):
        """Test writing to file."""
        builder = PlaybookBuilder()
        builder.set_playbook_name("Test")
        builder.add_task({"name": "Test", "debug": {"msg": "test"}})
        
        output_path = os.path.join(tmp_path, 'test_playbook.yml')
        result_path = builder.write_to_file(output_path)
        
        assert os.path.exists(result_path)
        with open(result_path, 'r') as f:
            content = yaml.safe_load(f)
        assert isinstance(content, list)
        assert content[0]['name'] == "Test"
    
    def test_list_modules(self):
        """Test listing modules."""
        builder = PlaybookBuilder()
        modules = builder.list_modules()
        assert isinstance(modules, list)
        assert len(modules) > 0
    
    def test_reset(self):
        """Test reset functionality."""
        builder = PlaybookBuilder()
        builder.set_playbook_name("Test")
        builder.add_task({"name": "Test", "debug": {"msg": "test"}})
        
        builder.reset()
        assert builder._playbook_data['name'] is None
        assert len(builder._playbook_data['tasks']) == 0
    
    def test_method_chaining(self):
        """Test method chaining."""
        builder = PlaybookBuilder()
        result = (builder
                 .set_playbook_name("Test")
                 .set_hosts("all")
                 .add_vars({"env": "prod"}))
        assert result is builder
        assert builder._playbook_data['name'] == "Test"


class TestUtils:
    """Test utility functions."""
    
    def test_generate_filename_basic(self):
        """Test basic filename generation."""
        filename = generate_filename('test')
        assert filename == 'test.yml'
    
    def test_generate_filename_with_extension(self):
        """Test filename generation with custom extension."""
        filename = generate_filename('test', extension='.yaml')
        assert filename == 'test.yaml'
    
    def test_generate_filename_timestamped(self):
        """Test timestamped filename generation."""
        filename = generate_filename('test', timestamped=True)
        assert filename.startswith('test_')
        assert filename.endswith('.yml')
        assert len(filename) > len('test.yml')
    
    def test_generate_filename_default(self):
        """Test default filename generation."""
        filename = generate_filename()
        assert filename == 'playbook.yml'
    
    def test_ensure_output_dir(self, tmp_path):
        """Test directory creation."""
        test_dir = os.path.join(tmp_path, 'test_output')
        result = ensure_output_dir(test_dir)
        assert os.path.exists(result)
        assert os.path.isdir(result)
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename('My Playbook') == 'my_playbook'
        assert sanitize_filename('Test/File!Name') == 'test_file_name'
        assert sanitize_filename('Multiple   Spaces') == 'multiple_spaces'
