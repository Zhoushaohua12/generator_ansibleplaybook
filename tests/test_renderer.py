import pytest
from playbook_generator.renderer import PlaybookRenderer
from jinja2 import TemplateNotFound


class TestPlaybookRenderer:
    """Tests for template rendering with parameters."""

    def test_render_basic_template(self, templates_dir, basic_params):
        """Test rendering a basic template with parameters."""
        renderer = PlaybookRenderer(templates_dir)
        result = renderer.render('basic', basic_params)
        
        assert isinstance(result, str)
        assert 'Deploy Web Application' in result
        assert 'webservers' in result
        assert '---' in result

    def test_render_with_default_values(self, templates_dir):
        """Test rendering with default values when parameters missing."""
        renderer = PlaybookRenderer(templates_dir)
        result = renderer.render('basic', {})
        
        assert isinstance(result, str)
        assert 'Basic Playbook' in result
        assert 'all' in result

    def test_render_template_with_loops(self, templates_dir, with_tasks_params):
        """Test rendering template with task loops."""
        renderer = PlaybookRenderer(templates_dir)
        result = renderer.render('with_tasks', with_tasks_params)
        
        assert isinstance(result, str)
        # Check for rendered tasks
        assert 'Install Apache' in result
        assert 'Start Apache service' in result
        assert 'Deploy configuration file' in result
        assert 'Install and Configure Services' in result

    def test_render_conditional_template(self, templates_dir, conditional_params):
        """Test rendering template with conditional clauses."""
        renderer = PlaybookRenderer(templates_dir)
        result = renderer.render('conditional', conditional_params)
        
        assert isinstance(result, str)
        # Check for when clauses
        assert 'when:' in result
        assert "environment_type == 'production'" in result
        assert 'enable_logging' in result

    def test_render_with_extension_in_name(self, templates_dir, basic_params):
        """Test rendering when template name includes .j2 extension."""
        renderer = PlaybookRenderer(templates_dir)
        result = renderer.render('basic.j2', basic_params)
        
        assert isinstance(result, str)
        assert 'Deploy Web Application' in result

    def test_render_nonexistent_template_raises_error(self, templates_dir):
        """Test that rendering a nonexistent template raises TemplateNotFound."""
        renderer = PlaybookRenderer(templates_dir)
        
        with pytest.raises(TemplateNotFound):
            renderer.render('nonexistent', {})

    def test_rendered_output_is_valid_yaml_structure(self, templates_dir, basic_params):
        """Test that rendered output has valid YAML structure."""
        renderer = PlaybookRenderer(templates_dir)
        result = renderer.render('basic', basic_params)
        
        # Check for YAML document marker
        assert result.strip().startswith('---')
        # Check for required playbook structure
        assert 'name:' in result
        assert 'hosts:' in result
        assert 'tasks:' in result

    def test_render_with_complex_parameters(self, templates_dir):
        """Test rendering with complex nested parameters."""
        renderer = PlaybookRenderer(templates_dir)
        params = {
            'playbook_name': 'Complex Playbook',
            'hosts': 'localhost',
            'tasks': [
                {
                    'name': 'Task 1',
                    'module': 'command',
                    'params': {'cmd': 'echo test'}
                }
            ]
        }
        result = renderer.render('with_tasks', params)
        
        assert 'Complex Playbook' in result
        assert 'Task 1' in result
        assert 'echo test' in result
