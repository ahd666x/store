import os
from django.core.wsgi import get_wsgi_application

settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
if not settings_module:
    raise RuntimeError(
        "DJANGO_SETTINGS_MODULE environment variable is not set. "
        "Set it to 'config.settings.dev' for development or "
        "'config.settings.production' for production."
    )

application = get_wsgi_application()
