"""
SQLAlchemy Base Class
Purpose: Declarative base for all ORM models
Author: BMAD BMM Agents Dev
Date: 2025-11-26
"""

from sqlalchemy.orm import declarative_base

# Create base class for all models
Base = declarative_base()

# Import all models here to ensure they're registered with Base
# This is needed for Alembic autogenerate to work
def import_models():
    """Import all models to register them with SQLAlchemy Base."""
    from app.models import site  # noqa
    from app.models import submission  # noqa
    from app.models import ai_result  # noqa
    from app.models import fraud_flag  # noqa
    from app.models import audit_log  # noqa
