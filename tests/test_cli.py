import os
import pytest
import yaml
from click.testing import CliRunner
from playbook_generator.cli import main, generate, list_templates


@pytest.fixture
def cli_runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


class TestCLI:
    """Tests for CLI functionality."""

    def test_main_help(self, cli_runner):
        """Test displaying help for main command."""
        result = cli_runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert 'Playbook Generator' in result.output

    def test_list_templates_command(self, cli_runner):
        """Test list-templates command."""
        result = cli_runner.invoke(main, ['list-templates'])
        
        assert result.exit_code == 0
        assert 'Available templates' in result.output
        assert 'basic' in result.output

    def test_list_templates_shows_all_templates(self, cli_runner):
        """Test that list-templates shows all available templates."""
        result = cli_runner.invoke(main, ['list-templates'])
        
        assert 'basic' in result.output
        assert 'with_tasks' in result.output
        assert 'conditional' in result.output

    def test_generate_help(self, cli_runner):
        """Test displaying help for generate command."""
        result = cli_runner.invoke(main, ['generate', '--help'])
        
        assert result.exit_code == 0
        assert 'Generate' in result.output or 'generate' in result.output

    def test_generate_with_template_argument(self, cli_runner, temp_output_dir):
        """Test generate command with template argument."""
        output_file = os.path.join(temp_output_dir, 'test.yml')
        
        result = cli_runner.invoke(main, [
            'generate',
            'basic',
            '-o', output_file
        ], input='\n\n')
        
        assert result.exit_code == 0
        assert 'generated' in result.output.lower()

    def test_generate_creates_output_file(self, cli_runner, temp_output_dir):
        """Test that generate command creates an output file."""
        output_file = os.path.join(temp_output_dir, 'playbook.yml')
        
        cli_runner.invoke(main, [
            'generate',
            'basic',
            '-o', output_file
        ], input='\n\n')
        
        assert os.path.exists(output_file)

    def test_generate_interactive_mode_with_template_selection(self, cli_runner, temp_output_dir):
        """Test interactive mode with template selection."""
        output_file = os.path.join(temp_output_dir, 'playbook.yml')
        
        result = cli_runner.invoke(main, [
            'generate',
            '-o', output_file
        ], input='1\n\n\n')
        
        assert result.exit_code == 0

    def test_generate_with_invalid_template(self, cli_runner):
        """Test generate with invalid template name."""
        result = cli_runner.invoke(main, [
            'generate',
            'nonexistent'
        ])
        
        assert result.exit_code != 0 or 'Error' in result.output

    def test_generate_from_file_command(self, cli_runner, temp_output_dir, fixtures_dir):
        """Test generate-from-file command."""
        output_file = os.path.join(temp_output_dir, 'playbook.yml')
        params_file = os.path.join(fixtures_dir, 'basic_params.yaml')
        
        result = cli_runner.invoke(main, [
            'generate-from-file',
            'basic',
            params_file,
            '-o', output_file
        ])
        
        assert result.exit_code == 0
        assert 'generated' in result.output.lower()

    def test_generate_from_file_creates_file(self, cli_runner, temp_output_dir, fixtures_dir):
        """Test that generate-from-file creates output file."""
        output_file = os.path.join(temp_output_dir, 'playbook.yml')
        params_file = os.path.join(fixtures_dir, 'basic_params.yaml')
        
        cli_runner.invoke(main, [
            'generate-from-file',
            'basic',
            params_file,
            '-o', output_file
        ])
        
        assert os.path.exists(output_file)

    def test_generate_from_file_with_tasks_template(self, cli_runner, temp_output_dir, fixtures_dir):
        """Test generate-from-file with tasks template."""
        output_file = os.path.join(temp_output_dir, 'playbook.yml')
        params_file = os.path.join(fixtures_dir, 'with_tasks_params.yaml')
        
        result = cli_runner.invoke(main, [
            'generate-from-file',
            'with_tasks',
            params_file,
            '-o', output_file
        ])
        
        assert result.exit_code == 0
        assert os.path.exists(output_file)
        
        with open(output_file, 'r') as f:
            content = f.read()
        assert 'Install Apache' in content

    def test_generate_from_file_with_conditional_template(self, cli_runner, temp_output_dir, fixtures_dir):
        """Test generate-from-file with conditional template."""
        output_file = os.path.join(temp_output_dir, 'playbook.yml')
        params_file = os.path.join(fixtures_dir, 'conditional_params.yaml')
        
        result = cli_runner.invoke(main, [
            'generate-from-file',
            'conditional',
            params_file,
            '-o', output_file
        ])
        
        assert result.exit_code == 0
        assert os.path.exists(output_file)
        
        with open(output_file, 'r') as f:
            content = f.read()
        assert 'when:' in content

    def test_generated_file_is_valid_yaml(self, cli_runner, temp_output_dir, fixtures_dir):
        """Test that generated file is valid YAML."""
        output_file = os.path.join(temp_output_dir, 'playbook.yml')
        params_file = os.path.join(fixtures_dir, 'basic_params.yaml')
        
        cli_runner.invoke(main, [
            'generate-from-file',
            'basic',
            params_file,
            '-o', output_file
        ])
        
        with open(output_file, 'r') as f:
            playbook = yaml.safe_load(f)
        
        assert isinstance(playbook, list)
        assert len(playbook) > 0

    def test_generate_with_custom_output_filename(self, cli_runner, temp_output_dir, fixtures_dir):
        """Test generate with custom output filename."""
        output_file = os.path.join(temp_output_dir, 'custom_name.yml')
        params_file = os.path.join(fixtures_dir, 'basic_params.yaml')
        
        cli_runner.invoke(main, [
            'generate-from-file',
            'basic',
            params_file,
            '-o', output_file
        ])
        
        assert os.path.exists(output_file)
        assert output_file.endswith('custom_name.yml')
