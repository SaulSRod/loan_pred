#python -m ETL.transformation.validation_loader
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.engine import Engine
import pandas as pd
from typing import Optional, Dict

def create_valid_accepted_hdma(engine: Engine) -> None:
    sql = text("""
    DROP VIEW IF EXISTS valid_accepted_hdma;           

    CREATE OR REPLACE VIEW valid_accepted_hdma AS
    SELECT
        loan_amount,
        loan_term, 
        interest_rate,
        income,
        debt_to_income_ratio,         

        CASE
            WHEN applicant_credit_score_type IN ('1','2') THEN 'Equifax'
            WHEN applicant_credit_score_type IN ('3','4') THEN 'FICO'
            WHEN applicant_credit_score_type IN ('5','6') THEN 'VantageScore'
            WHEN applicant_credit_score_type = '7' THEN 'Multiple Models'
            WHEN applicant_credit_score_type = '8' THEN 'Other Model'
            WHEN applicant_credit_score_type = '9' THEN 'Not Applicable'
            ELSE 'Exempt'
        END AS applicant_credit_score_type,

        CASE
            WHEN co_applicant_credit_score_type IN ('1','2') THEN 'Equifax'
            WHEN co_applicant_credit_score_type IN ('3','4','11') THEN 'FICO'
            WHEN co_applicant_credit_score_type IN ('5','6') THEN 'VantageScore'
            WHEN co_applicant_credit_score_type = '7' THEN 'Multiple Models'
            WHEN co_applicant_credit_score_type = '8' THEN 'Other Model'
            WHEN co_applicant_credit_score_type = '9' THEN 'Not Applicable'
            WHEN co_applicant_credit_score_type = '10' THEN 'No co-applicant'
            ELSE 'Exempt'
        END AS co_applicant_credit_score_type,

        activity_year,
        action_taken,
        preapproval,
        loan_to_value_ratio,
        total_loan_costs,
        derived_loan_product_type,
        loan_purpose

    FROM staging_accepted_hdma
    WHERE
        loan_amount IS NOT NULL
        AND loan_amount > 1000
        AND loan_term > 0
        AND income BETWEEN 0 AND 3000000
        AND debt_to_income_ratio <> ''
        AND debt_to_income_ratio IS NOT NULL
        AND applicant_credit_score_type IN ('1','2','3','4','5','6','7','8','9','11','1111')
        AND co_applicant_credit_score_type IN ('1','2','3','4','5','6','7','8','9','10','11','1111')
        AND activity_year = 2023
        AND action_taken = 1
        AND preapproval IN (1,2)
        AND loan_to_value_ratio BETWEEN 0 AND 130
        AND derived_loan_product_type IN (
            'Conventional:First Lien',
            'Conventional:Subordinate Lien',
            'FHA:First Lien',
            'FHA:Subordinate Lien',
            'VA:First Lien',
            'VA:Subordinate Lien',
            'FSA/RHS:First Lien',
            'FSA/RHS:Subordinate Lien'
        )
        AND loan_purpose <> ''
        AND loan_purpose IS NOT NULL;
    """)

    with engine.begin() as conn:
        conn.execute(sql)

def create_valid_rejected_hdma(engine: Engine) -> None:
    sql = text("""
    DROP VIEW IF EXISTS valid_rejected_hdma;           

    CREATE OR REPLACE VIEW valid_rejected_hdma AS
    SELECT
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

        CASE
            WHEN applicant_credit_score_type IN ('1','2') THEN 'Equifax'
            WHEN applicant_credit_score_type IN ('3','4') THEN 'FICO'
            WHEN applicant_credit_score_type IN ('5','6') THEN 'VantageScore'
            WHEN applicant_credit_score_type = '7' THEN 'Multiple Models'
            WHEN applicant_credit_score_type = '8' THEN 'Other Model'
            WHEN applicant_credit_score_type = '9' THEN 'Not Applicable'
            ELSE 'Exempt'
        END AS applicant_credit_score_type,

        CASE
            WHEN co_applicant_credit_score_type IN ('1','2') THEN 'Equifax'
            WHEN co_applicant_credit_score_type IN ('3','4','11') THEN 'FICO'
            WHEN co_applicant_credit_score_type IN ('5','6') THEN 'VantageScore'
            WHEN co_applicant_credit_score_type = '7' THEN 'Multiple Models'
            WHEN co_applicant_credit_score_type = '8' THEN 'Other Model'
            WHEN co_applicant_credit_score_type = '9' THEN 'Not Applicable'
            WHEN co_applicant_credit_score_type = '10' THEN 'No co-applicant'
            ELSE 'Exempt'
        END AS co_applicant_credit_score_type,

        CASE
            WHEN denial_reason_1 = '1' THEN 'Debt-to-income ratio'
            WHEN denial_reason_1 = '2' THEN 'Employment history'
            WHEN denial_reason_1 = '3' THEN 'Credit history'
            WHEN denial_reason_1 = '4' THEN 'Collateral'
            WHEN denial_reason_1 = '5' THEN 'Insufficient cash (downpayment, closing costs)'
            WHEN denial_reason_1 = '6' THEN 'Unverifiable information'
            WHEN denial_reason_1 = '7' THEN 'Credit application incomplete'
            WHEN denial_reason_1 = '8' THEN 'Mortgage insurance denied'
            WHEN denial_reason_1 IN ('9', '10') THEN 'Other'
        END AS denial_reason_1

    FROM staging_rejected_hdma
    WHERE 
        activity_year = 2023
        AND action_taken = 3     
        AND preapproval IN (1,2)
        AND loan_purpose <> ''
        AND loan_purpose IS NOT NULL
        AND loan_amount IS NOT NULL
        AND loan_amount > 0
        AND loan_term > 0
        AND loan_to_value_ratio > 0
        AND income BETWEEN 0 AND 3000000
        AND debt_to_income_ratio <> ''
        AND debt_to_income_ratio IS NOT NULL
        AND derived_loan_product_type IS NOT NULL
        AND derived_loan_product_type IN (
            'Conventional:First Lien',
            'Conventional:Subordinate Lien',
            'FHA:First Lien',
            'FHA:Subordinate Lien',
            'VA:First Lien',
            'VA:Subordinate Lien',
            'FSA/RHS:First Lien',
            'FSA/RHS:Subordinate Lien'
        )
        AND applicant_credit_score_type IN ('1','2','3','4','5','6','7','8','9','1111')
        AND co_applicant_credit_score_type IN ('1','2','3','4','5','6','7','8','9','10','1111')
        AND denial_reason_1 IN ('1','2','3','4','5','6','7','8','9','10');
    """)

    with engine.begin() as conn:
        conn.execute(sql)

def confirm_lengths(engine: Engine) -> None:
    queries = {
        "valid_accepted_hdma": "SELECT COUNT(*) FROM valid_accepted_hdma",
        "valid_accepted_kaggle": "SELECT COUNT(*) FROM valid_accepted_kaggle",
        "valid_rejected_hdma": "SELECT COUNT(*) FROM valid_rejected_hdma",
        "valid_rejected_kaggle": "SELECT COUNT(*) FROM valid_rejected_kaggle",
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