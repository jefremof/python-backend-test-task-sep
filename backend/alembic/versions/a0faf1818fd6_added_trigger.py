from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.scripts.activities_trigger import *

# revision identifiers, used by Alembic.
revision: str = 'a0faf1818fd6'
down_revision: Union[str, Sequence[str], None] = '1dd2a227ace4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(ACTIVITIES_DEPTH_TRIGGER)
    op.execute(SETUP_TRIGGER)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(DROP_TRIGGER)
    op.execute(DROP_FUNCTION)