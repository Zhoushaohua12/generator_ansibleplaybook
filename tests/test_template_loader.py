import os
import pytest
from playbook_generator.template_loader import TemplateLoader


class TestTemplateLoader:
    """Tests for template loading and validation."""

    def test_list_templates(self, templates_dir):
        """Test listing available templates."""
        loader = TemplateLoader(templates_dir)
        templates = loader.list_templates()
        
        assert isinstance(templates, list)
        assert len(templates) > 0
        assert 'basic' in templates
        assert 'with_tasks' in templates
        assert 'conditional' in templates

    def test_templates_are_sorted(self, templates_dir):
        """Test that templates are returned in sorted order."""
        loader = TemplateLoader(templates_dir)
        templates = loader.list_templates()
        
        assert templates == sorted(templates)

    def test_load_template_by_name_with_extension(self, templates_dir):
        """Test loading a template with .j2 extension."""
        loader = TemplateLoader(templates_dir)
        content = loader.load_template('basic.j2')
        
        assert isinstance(content, str)
        assert len(content) > 0
        assert 'Basic Playbook' in content or 'playbook_name' in content

    def test_load_template_by_name_without_extension(self, templates_dir):
        """Test loading a template without .j2 extension."""
        loader = TemplateLoader(templates_dir)
        content = loader.load_template('basic')
        
        assert isinstance(content, str)
        assert len(content) > 0

    def test_load_nonexistent_template_raises_error(self, templates_dir):
        """Test that loading a nonexistent template raises FileNotFoundError."""
        loader = TemplateLoader(templates_dir)
        
        with pytest.raises(FileNotFoundError):
            loader.load_template('nonexistent')

    def test_validate_existing_template(self, templates_dir):
        """Test validating an existing template."""
        loader = TemplateLoader(templates_dir)
        
        assert loader.validate_template('basic') is True
        assert loader.validate_template('with_tasks') is True
        assert loader.validate_template('conditional') is True

    def test_validate_nonexistent_template(self, templates_dir):
        """Test validating a nonexistent template."""
        loader = TemplateLoader(templates_dir)
        
        assert loader.validate_template('nonexistent') is False

    def test_get_template_schema_returns_dict(self, templates_dir):
        """Test that get_template_schema returns a dictionary."""
        loader = TemplateLoader(templates_dir)
        schema = loader.get_template_schema('basic')
        
        assert isinstance(schema, dict)

    def test_load_all_templates_without_error(self, templates_dir):
        """Test that all templates can be loaded without errors."""
        loader = TemplateLoader(templates_dir)
        templates = loader.list_templates()
        
        for template_name in templates:
            content = loader.load_template(template_name)
            assert isinstance(content, str)
            assert len(content) > 0
