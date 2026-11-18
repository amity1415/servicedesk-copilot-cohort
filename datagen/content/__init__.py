"""Authored content. Importing this package registers every knowledge-base topic.

The order of the imports below fixes the article numbering (KB-1001 onwards).
Add new modules at the end so existing articles keep their numbers.
"""

# isort: off
from datagen.content import identity  # noqa: F401
from datagen.content import network  # noqa: F401
from datagen.content import collab  # noqa: F401
from datagen.content import devices  # noqa: F401
from datagen.content import software  # noqa: F401
from datagen.content import people  # noqa: F401
from datagen.content import staff  # noqa: F401

# isort: on
from datagen.model import REGISTRY

TOPICS = tuple(REGISTRY.topics)
