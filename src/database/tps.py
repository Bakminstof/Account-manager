from datetime import datetime
from typing import Annotated

from sqlalchemy import JSON, TIMESTAMP, func
from sqlalchemy.orm import mapped_column

# =====================================|Annotated|====================================== #
created_at = Annotated[
    datetime,
    mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    ),
]

updated_at = Annotated[
    datetime,
    mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    ),
]

datetime_utc = Annotated[
    datetime,
    mapped_column(
        TIMESTAMP(timezone=True),
    ),
]

str_100 = Annotated[str, 100]
str_200 = Annotated[str, 200]
str_300 = Annotated[str, 300]
str_1000 = Annotated[str, 1000]

json_col = Annotated[dict, mapped_column(JSON)]
