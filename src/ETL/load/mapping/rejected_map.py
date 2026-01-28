from sqlalchemy import text
from sqlalchemy.engine import Engine

def map_rejected_hdma(engine: Engine) -> None:
    """
    - dataset_source is set to 'hdma'.
    - dti comes from cleaned debt_to_income_ratio TEXT.
    """

    sql = text(
        """
        INSERT INTO Rejected (
            income,
            dti,
            loan_to_value_ratio,
            loan_amount,
            term_months,
            denial_reason_1
        )
        SELECT 
            vrh.income,
            vrh.debt_to_income AS dti,
            vrh.loan_to_value_ratio,
            vrh.loan_amount,
            vrh.loan_term AS term_months,
            vrh.denial_reason_1
        FROM valid_rejected_hdma vrh;
        """
    )

    with engine.begin() as conn:
        conn.execute(sql)

def map_all_rejected_loans(engine: Engine) -> None:
    map_rejected_hdma(engine)