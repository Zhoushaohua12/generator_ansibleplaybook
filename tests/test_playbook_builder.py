import os
import pytest
import yaml
from playbook_generator.playbook_builder import PlaybookBuilder


class TestPlaybookBuilder:
    """Tests for playbook building and writing to disk."""

    def test_build_playbook(self, templates_dir, basic_params):
        """Test building a playbook from a template."""
        builder = PlaybookBuilder(templates_dir)
        result = builder.build_playbook('basic', basic_params)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert 'Deploy Web Application' in result

    def test_write_playbook_creates_file(self, templates_dir, temp_output_dir, basic_params):
        """Test that write_playbook creates a file."""
        builder = PlaybookBuilder(templates_dir)
        content = builder.build_playbook('basic', basic_params)
        
        output_path = os.path.join(temp_output_dir, 'test_playbook.yml')
        result_path = builder.write_playbook(content, output_path)
        
        assert os.path.exists(result_path)
        assert os.path.isfile(result_path)

    def test_write_playbook_returns_absolute_path(self, templates_dir, temp_output_dir, basic_params):
        """Test that write_playbook returns an absolute path."""
        builder = PlaybookBuilder(templates_dir)
        content = builder.build_playbook('basic', basic_params)
        
        output_path = os.path.join(temp_output_dir, 'test_playbook.yml')
        result_path = builder.write_playbook(content, output_path)
        
        assert os.path.isabs(result_path)

    def test_write_playbook_creates_directories(self, templates_dir, temp_output_dir):
        """Test that write_playbook creates necessary directories."""
        builder = PlaybookBuilder(templates_dir)
        content = "---\n- hosts: all\n  tasks: []\n"
        
        nested_path = os.path.join(temp_output_dir, 'subdir', 'nested', 'playbook.yml')
        result_path = builder.write_playbook(content, nested_path)
        
        assert os.path.exists(result_path)
        assert os.path.isdir(os.path.dirname(result_path))

    def test_write_playbook_content_matches_input(self, templates_dir, temp_output_dir):
        """Test that written file content matches input."""
        builder = PlaybookBuilder(templates_dir)
        content = "---\n- hosts: all\n  tasks: []\n"
        
        output_path = os.path.join(temp_output_dir, 'playbook.yml')
        builder.write_playbook(content, output_path)
        
        with open(output_path, 'r') as f:
            written_content = f.read()
        
        assert written_content == content

    def test_build_and_write_integration(self, templates_dir, temp_output_dir, basic_params):
        """Test build_and_write integration."""
        builder = PlaybookBuilder(templates_dir)
        output_path = os.path.join(temp_output_dir, 'playbook.yml')
        
        result_path = builder.build_and_write('basic', basic_params, output_path)
        
        assert os.path.exists(result_path)
        with open(result_path, 'r') as f:
            content = f.read()
        assert 'Deploy Web Application' in content

    def test_build_and_write_with_complex_template(self, templates_dir, temp_output_dir, 
                                                    with_tasks_params):
        """Test build_and_write with template containing loops."""
        builder = PlaybookBuilder(templates_dir)
        output_path = os.path.join(temp_output_dir, 'complex.yml')
        
        result_path = builder.build_and_write('with_tasks', with_tasks_params, output_path)
        
        assert os.path.exists(result_path)
        with open(result_path, 'r') as f:
            content = f.read()
        
        assert 'Install Apache' in content
        assert 'Start Apache service' in content

    def test_generated_playbook_is_valid_yaml(self, templates_dir, temp_output_dir, basic_params):
        """Test that generated playbook is valid YAML."""
        builder = PlaybookBuilder(templates_dir)
        output_path = os.path.join(temp_output_dir, 'playbook.yml')
        
        builder.build_and_write('basic', basic_params, output_path)
        
        with open(output_path, 'r') as f:
            playbook = yaml.safe_load(f)
        
        assert isinstance(playbook, list)
        assert len(playbook) > 0
        assert 'name' in playbook[0]
        assert 'hosts' in playbook[0]
        assert 'tasks' in playbook[0]

    def test_write_playbook_overwrites_existing_file(self, templates_dir, temp_output_dir):
        """Test that writing to existing file overwrites it."""
        builder = PlaybookBuilder(templates_dir)
        output_path = os.path.join(temp_output_dir, 'playbook.yml')
        
        content1 = "# First version\n"
        builder.write_playbook(content1, output_path)
        
        content2 = "# Second version\n"
        builder.write_playbook(content2, output_path)
        
        with open(output_path, 'r') as f:
            result = f.read()
        
        assert result == content2
        assert "First version" not in result
