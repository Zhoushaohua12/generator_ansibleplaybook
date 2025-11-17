import os
import click
from pathlib import Path
from playbook_generator.template_loader import TemplateLoader
from playbook_generator.playbook_builder import PlaybookBuilder


def get_templates_dir():
    """Get the templates directory path."""
    return os.path.join(os.path.dirname(__file__), 'templates')


@click.group()
def main():
    """Playbook Generator - Generate Ansible playbooks from templates."""
    pass


@main.command()
def list_templates():
    """List all available templates."""
    loader = TemplateLoader(get_templates_dir())
    templates = loader.list_templates()
    
    if not templates:
        click.echo("No templates found.")
        return
    
    click.echo("Available templates:")
    for template in templates:
        click.echo(f"  - {template}")


@main.command()
@click.argument('template', required=False)
@click.option('--output', '-o', default='playbook.yml', help='Output file path')
def generate(template, output):
    """Generate a playbook interactively or from arguments.
    
    TEMPLATE: Name of the template to use (optional for interactive mode).
    """
    loader = TemplateLoader(get_templates_dir())
    builder = PlaybookBuilder(get_templates_dir())
    
    if not template:
        # Interactive mode
        templates = loader.list_templates()
        if not templates:
            click.echo("No templates available.")
            return
        
        click.echo("\nAvailable templates:")
        for i, t in enumerate(templates, 1):
            click.echo(f"  {i}. {t}")
        
        choice = click.prompt("Select a template", type=click.IntRange(1, len(templates)))
        template = templates[choice - 1]
    
    if not loader.validate_template(template):
        click.echo(f"Error: Template '{template}' not found.")
        return
    
    # For now, use basic parameters
    parameters = {
        'playbook_name': click.prompt('Playbook name', default='My Playbook'),
        'hosts': click.prompt('Target hosts', default='all'),
    }
    
    try:
        output_path = builder.build_and_write(template, parameters, output)
        click.echo(f"✓ Playbook generated: {output_path}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@main.command()
@click.argument('template')
@click.argument('parameters', type=click.Path(exists=True))
@click.option('--output', '-o', default='playbook.yml', help='Output file path')
def generate_from_file(template, parameters, output):
    """Generate a playbook using parameters from a YAML file.
    
    TEMPLATE: Name of the template to use.
    PARAMETERS: Path to YAML file with parameters.
    """
    import yaml
    
    builder = PlaybookBuilder(get_templates_dir())
    loader = TemplateLoader(get_templates_dir())
    
    if not loader.validate_template(template):
        click.echo(f"Error: Template '{template}' not found.")
        return
    
    try:
        with open(parameters, 'r') as f:
            params = yaml.safe_load(f) or {}
        
        output_path = builder.build_and_write(template, params, output)
        click.echo(f"✓ Playbook generated: {output_path}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == '__main__':
    main()
