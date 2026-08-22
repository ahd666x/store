#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
    if not settings_module:
        raise RuntimeError(
            "DJANGO_SETTINGS_MODULE environment variable is not set. "
            "Set it to 'config.settings.dev' for development or "
            "'config.settings.production' for production."
        )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
