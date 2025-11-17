from setuptools import setup, find_packages

setup(
    name="playbook-generator",
    version="0.1.0",
    description="A CLI tool for generating Ansible playbooks from templates",
    author="Engine Labs",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "jinja2>=3.0.0",
        "pyyaml>=5.0.0",
    ],
    entry_points={
        "console_scripts": [
            "playbook-gen=playbook_generator.cli:main",
        ],
    },
)
