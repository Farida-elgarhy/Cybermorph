from setuptools import setup, find_packages
import os

long_description = ""
if os.path.exists('README.md'):
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='cybermorph',
    version='1.0.0',
    description='CyberMorph: Fully Automated Environment Replication',
    packages=find_packages(where='.'),
    py_modules=[
        'cybermorph',
        'cybermorph_auto',
        'cybermorph_auto_config',
        'cybermorph_init',
        'cybermorph_agent_installer',
        'cybermorph_discovery',
        'cybermorph_dlp',
        'cybermorph_sanitization',
        'cybermorph_docker_provisioner',
        'cybermorph_n8n_orchestrator',
    ],
    python_requires='>=3.8',
    install_requires=[
        'pyyaml>=6.0',
        'paramiko>=3.0',
        'docker>=6.0',
        'boto3>=1.26',
        'presidio-analyzer>=2.2',
        'spacy>=3.5',
        'faker>=15.0',
        'requests>=2.28',
    ],
    entry_points={
        'console_scripts': [
            'cybermorph-auto=cybermorph_auto:main',
        ],
    },
)