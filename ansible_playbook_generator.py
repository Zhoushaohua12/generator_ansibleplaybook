#!/usr/bin/env python3
"""
Ansible Playbook Generator - Main entry point

This script provides both interactive and CLI-driven generation of Ansible playbooks
from Jinja2 templates. It supports menu-based interaction and command-line arguments
for scripting scenarios.
"""

import sys
import os
import argparse
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add the playbook_generator package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playbook_generator.template_loader import TemplateLoader
from playbook_generator.playbook_builder import PlaybookBuilder
from playbook_generator.renderer import PlaybookRenderer


class PlaybookGeneratorCLI:
    """Main CLI interface for the playbook generator."""
    
    def __init__(self):
        """Initialize the CLI with required components."""
        self.templates_dir = os.path.join(os.path.dirname(__file__), 'playbook_generator', 'templates')
        self.loader = TemplateLoader(self.templates_dir)
        self.builder = PlaybookBuilder(self.templates_dir)
        self.renderer = PlaybookRenderer(self.templates_dir)
        
    def get_module_categories(self) -> Dict[str, List[str]]:
        """Get module categories and available modules from templates.
        
        Returns:
            Dictionary mapping categories to list of modules.
        """
        templates = self.loader.list_templates()
        
        # Categorize templates based on their names and content
        categories = {
            "Basic": [],
            "Advanced": [],
            "Conditional": [],
            "Multi-task": []
        }
        
        for template in templates:
            if template == "basic":
                categories["Basic"].append(template)
            elif template == "conditional":
                categories["Conditional"].append(template)
            elif template == "with_tasks":
                categories["Multi-task"].append(template)
            else:
                categories["Advanced"].append(template)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def display_menu(self) -> Dict[str, Any]:
        """Display the main menu interface.
        
        Returns:
            Dictionary mapping menu choices to categories and modules.
        """
        print("\n" + "="*50)
        print("Ansible Playbook Generator")
        print("="*50)
        
        categories = self.get_module_categories()
        
        if not categories:
            print("No templates available.")
            return {}
        
        print("\nAvailable Module Categories:")
        category_map = {}
        idx = 1
        
        for category, modules in categories.items():
            print(f"\n{idx}. {category}")
            category_map[str(idx)] = (category, modules)
            
            for i, module in enumerate(modules, 1):
                print(f"   {idx}.{i} {module}")
                category_map[f"{idx}.{i}"] = (category, [module])
            
            idx += 1
        
        return category_map
    
    def collect_parameters_interactive(self, template_name: str) -> Dict[str, Any]:
        """Collect parameters for a template through interactive prompts.
        
        Args:
            template_name: Name of the template to collect parameters for.
            
        Returns:
            Dictionary of parameters collected from user input.
        """
        print(f"\n--- Configuring {template_name} ---")
        params = {}
        
        # Basic parameters that all templates need
        params['playbook_name'] = input("Playbook name [My Playbook]: ").strip() or "My Playbook"
        params['hosts'] = input("Target hosts [all]: ").strip() or "all"
        
        # Template-specific parameters
        if template_name == "basic":
            # Basic template needs no additional parameters
            pass
            
        elif template_name == "with_tasks":
            params['tasks'] = self.collect_tasks_interactive()
            
        elif template_name == "conditional":
            params['tasks'] = self.collect_tasks_interactive(include_conditions=True)
            params['vars'] = self.collect_variables_interactive()
        
        # Ask about advanced options
        if self.confirm("Add custom variables?"):
            params['vars'] = params.get('vars', {})
            params['vars'].update(self.collect_variables_interactive())
        
        return params
    
    def collect_tasks_interactive(self, include_conditions: bool = False) -> List[Dict[str, Any]]:
        """Collect tasks interactively from user input.
        
        Args:
            include_conditions: Whether to prompt for when conditions.
            
        Returns:
            List of task dictionaries.
        """
        tasks = []
        
        while True:
            print(f"\n--- Task {len(tasks) + 1} ---")
            task_name = input("Task name: ").strip()
            if not task_name:
                break
            
            module = input("Ansible module [debug]: ").strip() or "debug"
            
            # Collect module parameters
            task_params = {}
            while True:
                param_name = input("Parameter name (empty to finish): ").strip()
                if not param_name:
                    break
                param_value = input(f"Parameter value for {param_name}: ").strip()
                task_params[param_name] = param_value
            
            task = {
                'name': task_name,
                'module': module,
                'params': task_params
            }
            
            # Add condition if requested
            if include_conditions:
                condition = input("When condition (optional): ").strip()
                if condition:
                    task['when'] = condition
            
            # Add loop if requested
            if self.confirm("Add loop to this task?"):
                loop_type = input("Loop type [list/items]: ").strip() or "items"
                loop_var = input("Loop variable/items: ").strip()
                task['loop'] = loop_var
                if loop_type != "items":
                    task['loop_control'] = {'label': loop_type}
            
            tasks.append(task)
            
            if not self.confirm("Add another task?"):
                break
        
        return tasks
    
    def collect_variables_interactive(self) -> Dict[str, Any]:
        """Collect variables interactively from user input.
        
        Returns:
            Dictionary of variables.
        """
        variables = {}
        
        while True:
            var_name = input("Variable name (empty to finish): ").strip()
            if not var_name:
                break
            
            var_value = input(f"Variable value for {var_name}: ").strip()
            
            # Try to parse as YAML for proper typing
            try:
                variables[var_name] = yaml.safe_load(var_value)
            except yaml.YAMLError:
                variables[var_name] = var_value
        
        return variables
    
    def confirm(self, message: str) -> bool:
        """Ask for yes/no confirmation.
        
        Args:
            message: Confirmation message to display.
            
        Returns:
            True if user confirms, False otherwise.
        """
        response = input(f"{message} [y/N]: ").strip().lower()
        return response in ('y', 'yes')
    
    def preview_playbook(self, content: str) -> None:
        """Display a preview of the generated playbook.
        
        Args:
            content: The playbook content to preview.
        """
        print("\n--- Playbook Preview ---")
        print(content)
        print("--- End Preview ---\n")
    
    def interactive_mode(self) -> None:
        """Run the generator in interactive mode."""
        print("Starting interactive mode...")
        
        # Display menu and get selection
        category_map = self.display_menu()
        if not category_map:
            return
        
        while True:
            try:
                choice = input("\nSelect option (e.g., 1, 1.1): ").strip()
                if not choice:
                    continue
                
                if choice not in category_map:
                    print("Invalid selection. Please try again.")
                    continue
                
                category, modules = category_map[choice]
                
                # If a specific module was selected
                if len(modules) == 1:
                    template_name = modules[0]
                    parameters = self.collect_parameters_interactive(template_name)
                    
                    # Generate playbook
                    content = self.builder.build_playbook(template_name, parameters)
                    self.preview_playbook(content)
                    
                    if self.confirm("Save this playbook?"):
                        output_path = self.get_output_path()
                        self.builder.write_playbook(content, output_path)
                        print(f"✓ Playbook saved to: {output_path}")
                    
                    return
                
                # If a category was selected, allow selecting multiple modules
                else:
                    print(f"\nAvailable modules in {category}:")
                    for i, module in enumerate(modules, 1):
                        print(f"  {i}. {module}")
                    
                    selected_indices = input("Select modules (comma-separated, or 'all'): ").strip()
                    
                    if selected_indices.lower() == 'all':
                        selected_modules = modules
                    else:
                        try:
                            indices = [int(x.strip()) - 1 for x in selected_indices.split(',')]
                            selected_modules = [modules[i] for i in indices if 0 <= i < len(modules)]
                        except (ValueError, IndexError):
                            print("Invalid selection.")
                            continue
                    
                    if not selected_modules:
                        print("No modules selected.")
                        continue
                    
                    # Generate individual playbooks for each selected module
                    for module in selected_modules:
                        parameters = self.collect_parameters_interactive(module)
                        
                        # Generate playbook
                        content = self.builder.build_playbook(module, parameters)
                        self.preview_playbook(content)
                        
                        if self.confirm(f"Save {module} playbook?"):
                            output_path = self.get_output_path(f"{module}_playbook.yml")
                            self.builder.write_playbook(content, output_path)
                            print(f"✓ Playbook saved to: {output_path}")
                    
                    return
                    
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                return
            except Exception as e:
                print(f"Error: {e}")
                return
    
    def get_output_path(self, default_name: str = "playbook.yml") -> str:
        """Get output path from user, defaulting to generated_playbooks directory.
        
        Args:
            default_name: Default filename to use.
            
        Returns:
            Absolute path to output file.
        """
        # Ensure generated_playbooks directory exists
        output_dir = os.path.join(os.getcwd(), "generated_playbooks")
        os.makedirs(output_dir, exist_ok=True)
        
        default_path = os.path.join(output_dir, default_name)
        user_path = input(f"Output path [{default_path}]: ").strip()
        
        if not user_path:
            return default_path
        
        # If relative path, make it relative to current directory
        if not os.path.isabs(user_path):
            user_path = os.path.join(os.getcwd(), user_path)
        
        return user_path
    
    def cli_mode(self, args) -> None:
        """Run the generator in CLI mode with arguments.
        
        Args:
            args: Parsed command line arguments.
        """
        if args.modules:
            # Non-interactive mode with specified modules
            templates = args.modules.split(',')
            parameters = {}
            
            # Load variables file if provided
            if args.vars_file:
                with open(args.vars_file, 'r') as f:
                    parameters.update(yaml.safe_load(f) or {})
            
            # Add basic parameters only if not already provided
            if 'playbook_name' not in parameters:
                parameters['playbook_name'] = args.playbook_name or 'Generated Playbook'
            if 'hosts' not in parameters:
                parameters['hosts'] = args.inventory or 'all'
            
            for template in templates:
                template = template.strip()
                if not self.loader.validate_template(template):
                    print(f"Warning: Template '{template}' not found, skipping.")
                    continue
                
                try:
                    content = self.builder.build_playbook(template, parameters)
                    
                    # Generate unique output path for each template
                    if args.output:
                        if len(templates) == 1:
                            output_path = args.output
                        else:
                            # Append template name to avoid overwriting
                            base_name = os.path.splitext(args.output)[0]
                            extension = os.path.splitext(args.output)[1] or '.yml'
                            output_path = f"{base_name}_{template}{extension}"
                    else:
                        output_path = f"generated_playbooks/{template}_playbook.yml"
                    
                    output_path = self.builder.write_playbook(content, output_path)
                    print(f"✓ Generated {template} playbook: {output_path}")
                except Exception as e:
                    print(f"Error generating {template}: {e}")
        
        else:
            # No modules specified, fall back to interactive mode
            print("No modules specified. Starting interactive mode...")
            self.interactive_mode()
    
    def main(self) -> None:
        """Main entry point for the application."""
        parser = argparse.ArgumentParser(
            description="Generate Ansible playbooks from templates",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Interactive mode
  python ansible_playbook_generator.py
  
  # Non-interactive mode
  python ansible_playbook_generator.py --modules basic,conditional --output my_playbook.yml
  
  # With variables file
  python ansible_playbook_generator.py --modules with_tasks --vars-file vars.yml --inventory production
            """
        )
        
        parser.add_argument(
            '--modules', '-m',
            help='Comma-separated list of modules to use (e.g., basic,conditional,with_tasks)'
        )
        
        parser.add_argument(
            '--output', '-o',
            help='Output file path (default: generated_playbooks/{module}_playbook.yml)'
        )
        
        parser.add_argument(
            '--inventory', '-i',
            help='Target inventory/hosts (default: all)'
        )
        
        parser.add_argument(
            '--vars-file', '-v',
            help='Path to YAML file containing variables'
        )
        
        parser.add_argument(
            '--playbook-name', '-n',
            help='Name for the generated playbook'
        )
        
        parser.add_argument(
            '--interactive', '--int',
            action='store_true',
            help='Force interactive mode'
        )
        
        args = parser.parse_args()
        
        if args.interactive or not args.modules:
            self.interactive_mode()
        else:
            self.cli_mode(args)


def main():
    """Entry point when script is run directly."""
    try:
        cli = PlaybookGeneratorCLI()
        cli.main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()