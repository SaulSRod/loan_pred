from sqlalchemy import text
from sqlalchemy.engine import Engine

def map_rejected_hdma(engine: Engine) -> None:
    """
    - dataset_source is set to 'hdma'
    """

    sql = text(
        """
        INSERT INTO Rejected (
            borrower_id,
            denial_reason_1
        )
        SELECT 
            b.borrower_id,
            vrh.denial_reason_1 AS denial_reason_1
        FROM valid_rejected_hdma vrh

        INNER JOIN Borrowers b 
        ON vrh.rejected_id = b.rejected_id
        ON CONFLICT (borrower_id) DO NOTHING;

        ALTER TABLE Borrowers DROP COLUMN IF EXISTS rejected_id; 
        """
    )

    with engine.begin() as conn:
        conn.execute(sql)

def map_all_rejected_loans(engine: Engine) -> None:
    map_rejected_hdma(engine)