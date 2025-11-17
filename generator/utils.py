"""Helper utilities for naming output files and managing directories."""

import os
from datetime import datetime
from pathlib import Path


def generate_filename(base_name: str = None, timestamped: bool = False, 
                     extension: str = '.yml') -> str:
    """Generate an output filename with optional timestamp.
    
    Args:
        base_name: Base name for the file. If None, uses 'playbook'.
        timestamped: If True, append timestamp to filename.
        extension: File extension (default: '.yml').
        
    Returns:
        Generated filename.
        
    Examples:
        >>> generate_filename('webserver')
        'webserver.yml'
        >>> generate_filename('webserver', timestamped=True)
        'webserver_20231117_143025.yml'
        >>> generate_filename(timestamped=True)
        'playbook_20231117_143025.yml'
    """
    if base_name is None:
        base_name = 'playbook'
    
    if not extension.startswith('.'):
        extension = '.' + extension
    
    base_name = base_name.replace(extension, '')
    
    if timestamped:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{base_name}_{timestamp}{extension}"
    
    return f"{base_name}{extension}"


def ensure_output_dir(directory: str = None) -> str:
    """Ensure the output directory exists.
    
    Args:
        directory: Directory path. If None, uses 'generated_playbooks'.
        
    Returns:
        Absolute path to the directory.
        
    Raises:
        OSError: If directory cannot be created.
    """
    if directory is None:
        directory = 'generated_playbooks'
    
    abs_directory = os.path.abspath(directory)
    
    os.makedirs(abs_directory, exist_ok=True)
    
    return abs_directory


def get_output_path(filename: str = None, directory: str = None, 
                   timestamped: bool = False) -> str:
    """Get the full output path for a playbook file.
    
    Args:
        filename: Filename or None to auto-generate.
        directory: Output directory or None for default.
        timestamped: Whether to add timestamp to filename.
        
    Returns:
        Absolute path to output file.
        
    Examples:
        >>> get_output_path('my_playbook.yml')
        '/path/to/generated_playbooks/my_playbook.yml'
        >>> get_output_path(timestamped=True)
        '/path/to/generated_playbooks/playbook_20231117_143025.yml'
    """
    output_dir = ensure_output_dir(directory)
    
    if filename is None:
        filename = generate_filename(timestamped=timestamped)
    elif timestamped and datetime.now().strftime('%Y%m%d') not in filename:
        base_name = os.path.splitext(filename)[0]
        extension = os.path.splitext(filename)[1] or '.yml'
        filename = generate_filename(base_name, timestamped=True, extension=extension)
    
    return os.path.join(output_dir, filename)


def sanitize_filename(name: str) -> str:
    """Sanitize a string to be used as a filename.
    
    Args:
        name: String to sanitize.
        
    Returns:
        Sanitized filename-safe string.
        
    Examples:
        >>> sanitize_filename('My Playbook!')
        'my_playbook'
        >>> sanitize_filename('Web/Server Deploy')
        'web_server_deploy'
    """
    name = name.lower()
    name = ''.join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in name)
    name = '_'.join(name.split())
    name = name.strip('_')
    
    return name
