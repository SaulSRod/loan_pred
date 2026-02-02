from sqlalchemy import text
from sqlalchemy.engine import Engine

def map_accepted_borrowers(engine: Engine) -> None:
    # debt_to_income_ratio staging is TEXT --> strip non-numeric chars and cast to numeric
    sql = text("""
        INSERT INTO Borrowers (
            activity_year,
            action_taken,
            preapproval,
            loan_purpose,
            loan_amount,
            loan_term,

            applicant_credit_score_type,
            co_applicant_credit_score_type,

            loan_to_value_ratio,
            income,
            debt_to_income_ratio,    
            derived_loan_product_type
        )
        SELECT DISTINCT
            vah.activity_year,
            vah.action_taken,
            vah.preapproval,
            vah.loan_purpose,
            vah.loan_amount,
            vah.loan_term,   

            vah.applicant_credit_score_type,
            vah.co_applicant_credit_score_type,
            
            vah.loan_to_value_ratio,
            vah.income,
            vah.debt_to_income_ratio,
            vah.derived_loan_product_type
            
        FROM valid_accepted_hdma vah;
    """)

    with engine.begin() as conn:
        conn.execute(sql)


def map_rejected_borrowers(engine: Engine) -> None:
    # debt_to_income_ratio staging is TEXT --> strip non-numeric chars and cast to numeric
    sql = text("""
        INSERT INTO Borrowers (
            rejected_id,
            activity_year,
            action_taken,
            preapproval,
            loan_purpose,
            loan_amount,
            loan_term,

            applicant_credit_score_type,
            co_applicant_credit_score_type,

            loan_to_value_ratio,
            income,
            debt_to_income_ratio,    
            derived_loan_product_type
        )
        SELECT DISTINCT
            vrh.rejected_id,
            vrh.activity_year,
            vrh.action_taken,
            vrh.preapproval,
            vrh.loan_purpose,
            vrh.loan_amount,
            vrh.loan_term,   

            vrh.applicant_credit_score_type,
            vrh.co_applicant_credit_score_type,
            
            vrh.loan_to_value_ratio,
            vrh.income,
            vrh.debt_to_income_ratio,
            vrh.derived_loan_product_type
               
        FROM valid_rejected_hdma vrh;
    """)

    with engine.begin() as conn:
        conn.execute(sql)

def map_all_borrowers(engine: Engine) -> None:
    map_accepted_borrowers(engine)
    map_rejected_borrowers(engine)