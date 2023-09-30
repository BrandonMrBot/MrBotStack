import logging
from {{ cookiecutter.project_name }}.models import (
    Country,
    map_from_schema,
)

__all__ = [
    "get_all_countries",
]

log = logging.getLogger("{{ cookiecutter.project_name }}")


def get_all_countries(request):

    res = map_from_schema(
        request.dbsession.query(Country).order_by(Country.cnty_name).all()
    )

    return res
