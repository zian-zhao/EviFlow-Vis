#!/usr/bin/env python
"""
Django entrypoint for the EviFlow-Vis / cs-workbench project.

- Settings module: ``vizforge.settings`` (see ``vizforge/`` package).
- Typical local run: ``python manage.py runserver 0.0.0.0:8000`` then open ``/cs-workbench/``.

The block below is the stock Django dispatcher; only ``DJANGO_SETTINGS_MODULE`` is project-specific.
"""
import os
import sys


def main():
    """Dispatch manage.py subcommands to Django."""
    try:
        from pathlib import Path
        from dotenv import load_dotenv

        load_dotenv(Path(__file__).resolve().parent / ".env")
    except ImportError:
        pass
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vizforge.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
