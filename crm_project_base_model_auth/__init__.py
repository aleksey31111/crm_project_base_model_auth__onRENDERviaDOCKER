# crm_project_base_model_auth1/__init__.py
from .local_celery_script import app as celery_app

__all__ = ('celery_app',)