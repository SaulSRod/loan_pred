"""
Goal: given a loan application, predict whether the loan will default.
Target: Will the loan default? good/bad 0/1

    -- loan_status values
bad -- Charged Off, Default, Late (31-120 days)
good -- Fully Paid Current

dropped -- empty/NULL, Does not meet the credit policy. Status:, In Grace Period, Late (16-30 days)
"""

"""
OUTPUT/PRINT

Created view: accepted_loans_ml_training
accepted_loans_ml_training -> total=3750051, is_rejected(0)=2771562, is_rejected(1)=978489

"""

from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

VIEW_NM = "accepted_loans_ml_training"

def create_accepted_loans_training_view(engine: Optional[Engine] = None) -> None:
    if engine is None:
        engine = create_engine("postgresql+psycopg2:///credit_risk")

    ddl = text(
        f"""
        DROP VIEW IF EXISTS {VIEW_NM};

        CREATE VIEW {VIEW_NM} AS
        SELECT
            -- ids, primary key
            b.borrower_id,

            -- accepted/rejected column
            CASE
                -- accepted
                WHEN b.action_taken = 1
                    THEN 0
                -- rejected
                WHEN b.action_taken = 3
                    THEN 1
                ELSE NULL
            END as is_rejected,

            -- numerics
            b.loan_amount,
            b.debt_to_income_ratio,
            b.income,
            b.loan_term,

            -- cats
            b.loan_purpose
        FROM Borrowers b
        WHERE b.activity_year = 2023;
        """
    )

    with engine.connect() as conn:
        conn.execute(ddl)
        conn.commit()

    print(f"Created view: {VIEW_NM}")

# row counts for total/pos/nega
def preview_training_counts(engine: Optional[Engine] = None) -> None:
    if engine is None:
        engine = create_engine("postgresql+psycopg2:///credit_risk")

    with engine.connect() as conn:
        total = conn.execute(
            text(f"SELECT COUNT(*) FROM {VIEW_NM}")
        ).scalar()

        positives = conn.execute(
            text(f"SELECT COUNT(*) FROM {VIEW_NM} WHERE is_rejected = 0")
        ).scalar()

        negatives = conn.execute(
            text(f"SELECT COUNT(*) FROM {VIEW_NM} WHERE is_rejected = 1")
        ).scalar()

    print(
        f"{VIEW_NM} -> total={total}, "
        f"is_rejected(0)={positives}, is_rejected(1)={negatives}"
    )

if __name__ == "__main__":
    engine = create_engine("postgresql+psycopg2:///credit_risk")
    create_accepted_loans_training_view(engine)
    preview_training_counts(engine)
