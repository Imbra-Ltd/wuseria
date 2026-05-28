"""Model-name to file-slug conversion.

Every brand tool converts a lens model name into a folder slug the same
way — lowercase, drop the slash in "f/", replace any run of non-alphanumeric
characters with a single hyphen — differing only by a brand prefix. This is
the one shared implementation.
"""

import re


def model_to_slug(prefix: str, model: str) -> str:
    """Convert a model name to a prefixed file slug.

    >>> model_to_slug("tokina", "atx-m 23mm f/1.4 X")
    'tokina-atx-m-23mm-f1-4-x'
    """
    slug = model.lower().replace("f/", "f")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return f"{prefix}-{slug}"
