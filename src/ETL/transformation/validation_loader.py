#python -m ETL.transformation.validation_loader
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.engine import Engine

def create_valid_accepted_hdma(engine: Engine) -> None:
    sql = text("""
    DROP VIEW IF EXISTS valid_accepted_hdma;           

    CREATE OR REPLACE VIEW valid_accepted_hdma AS
    SELECT
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

    FROM staging_accepted_hdma
    WHERE
        loan_amount IS NOT NULL
        AND loan_amount > 1000
        AND loan_term > 0
        AND income BETWEEN 0 AND 4000000
        AND debt_to_income_ratio IS NOT NULL
        AND debt_to_income_ratio BETWEEN 0 AND 100
        AND applicant_credit_score_type IN (1,2,3,4,5,6,7,8,9,10,11,1111)
        AND co_applicant_credit_score_type IN (1,2,3,4,5,6,7,8,9,10,11,1111)
        AND activity_year = 2023
        AND action_taken = 1
        AND preapproval IN (1,2)
        AND loan_to_value_ratio BETWEEN 0 AND 100
        AND derived_loan_product_type IN (
            'Conventional:First Lien',
            'FHA:First Lien',
            'VA:First Lien',
            'FSA/RHS:First Lien'
        )
        AND loan_purpose IN (1,31,32);
    """)

    with engine.begin() as conn:
        conn.execute(sql)

def create_valid_rejected_hdma(engine: Engine) -> None:
    sql = text("""
    DROP VIEW IF EXISTS valid_rejected_hdma;           

    CREATE OR REPLACE VIEW valid_rejected_hdma AS
    SELECT
        rejected_id,
        activity_year,
        action_taken,      
        preapproval,
        loan_purpose,
        loan_amount,
        loan_term,
        loan_to_value_ratio,
        income,
        debt_to_income_ratio,   
        derived_loan_product_type,
        applicant_credit_score_type,
        co_applicant_credit_score_type,
        denial_reason_1

    FROM staging_rejected_hdma
    WHERE 
        activity_year = 2023
        AND action_taken = 3     
        AND preapproval IN (1,2)
        AND loan_purpose IN (1,31,32)
        AND loan_amount > 0
        AND loan_term > 0
        AND loan_to_value_ratio > 0
        AND income BETWEEN 0 AND 4000000
        AND debt_to_income_ratio IS NOT NULL
        AND derived_loan_product_type IN (
            'Conventional:First Lien',
            'FHA:First Lien',
            'VA:First Lien',
            'FSA/RHS:First Lien'
        )
        AND applicant_credit_score_type IN (1,2,3,4,5,6,7,8,9,10,11,1111)
        AND co_applicant_credit_score_type IN (1,2,3,4,5,6,7,8,9,10,11,1111)
        AND denial_reason_1 IN (1,2,3,4,5,6,7,8,9,10);
    """)

    with engine.begin() as conn:
        conn.execute(sql)

def confirm_lengths(engine: Engine) -> None:
    queries = {
        "valid_accepted_hdma": "SELECT COUNT(*) FROM valid_accepted_hdma",
        "valid_rejected_hdma": "SELECT COUNT(*) FROM valid_rejected_hdma",
    }

    with engine.connect() as conn:
        for name, query in queries.items():
            result = conn.execute(text(query)).scalar()
            print(f"{name} size -> {result}")

if __name__ == "__main__":
    engine = create_engine("postgresql+psycopg2:///credit_risk")
    try:

        print("=== Loading VALID HDMA accepted table ===")
        create_valid_accepted_hdma(engine)

        print("=== Loading VALID HDMA rejected table ===")
        create_valid_rejected_hdma(engine)

        print("=== ALL VALID TABLES WERE LOADED ===")
        confirm_lengths(engine)
    
    except Exception as e:
        print(f"Error when trying to validate data: {e}")