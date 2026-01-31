from sqlalchemy import text
from sqlalchemy.engine import Engine

def map_accepted_borrowers(engine: Engine) -> None:
    # debt_to_income_ratio staging is TEXT --> strip non-numeric chars and cast to numeric
    sql = text("""
        INSERT INTO Borrowers (
            action_taken                    SMALLINT,
            loan_purpose                    SMALLINT,
            preapproval                     SMALLINT,
            applicant_credit_score_type     SMALLINT,     
            derived_loan_product_type       TEXT
        )
        SELECT DISTINCT
            vah.action_taken,
            vah.loan_purpose,
            vah.preapproval,
            vah.applicant_credit_score_type,
            vah.derived_loan_product_type
            
        FROM valid_accepted_hdma vah;
    """)

    with engine.begin() as conn:
        conn.execute(sql)


def map_rejected_borrowers(engine: Engine) -> None:
    # debt_to_income_ratio staging is TEXT --> strip non-numeric chars and cast to numeric
    sql = text("""
        INSERT INTO Borrowers (
            action_taken                    SMALLINT,
            loan_purpose                    SMALLINT,
            preapproval                     SMALLINT,
            applicant_credit_score_type     SMALLINT,     
            derived_loan_product_type       TEXT
        )
        SELECT DISTINCT
            vrh.action_taken,
            vrh.loan_purpose,
            vrh.preapproval,
            vrh.applicant_credit_score_type,
            vrh.derived_loan_product_type
               
        FROM valid_rejected_hdma vrh;
    """)

    with engine.begin() as conn:
        conn.execute(sql)

def map_all_borrowers(engine: Engine) -> None:
    map_accepted_borrowers(engine)
    map_rejected_borrowers(engine)