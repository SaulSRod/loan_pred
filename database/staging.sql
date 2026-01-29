-- psql -d credit_risk -f database/staging.sql

-- psql -d credit_risk
-- \dt

DROP TABLE IF EXISTS staging_accepted_hdma CASCADE;
DROP TABLE IF EXISTS staging_rejected_hdma CASCADE;

CREATE TABLE staging_accepted_hdma (
    -- ['activity_year', 'action_taken', 'preapproval', 'loan_purpose', 'loan_amount', 'loan_term', 'applicant_credit_score_type',
    -- 'co_applicant_credit_score_type' , 'loan_to_value_ratio', 'income', 'debt_to_income_ratio', 'derived_loan_product_type']
    activity_year                   SMALLINT,
    action_taken                    SMALLINT,
    preapproval                     SMALLINT,
    loan_purpose                    SMALLINT,
    loan_amount                     DECIMAL (16,4),
    loan_term                       DECIMAL (16,4),
    applicant_credit_score_type     SMALLINT,   

    co_applicant_credit_score_type  SMALLINT,
    loan_to_value_ratio             DECIMAL (16,4),
    income                          DECIMAL (16,4),
    debt_to_income_ratio            DECIMAL (16,4),    
    derived_loan_product_type       TEXT
    
);

CREATE TABLE staging_rejected_hdma (
    -- ['activity_year', 'action_taken', 'preapproval', 'loan_purpose', 'loan_amount', 'loan_term', 'applicant_credit_score_type', 'co_applicant_credit_score_type', 'denial_reason_1', 'loan_to_value_ratio', 'income', 'debt_to_income_ratio', 'derived_loan_product_type']
    activity_year                   SMALLINT,
    action_taken                    SMALLINT,
    preapproval                     SMALLINT,
    loan_purpose                    SMALLINT,
    loan_amount                     DECIMAL (18,4),
    loan_term                       DECIMAL (18,4),
    applicant_credit_score_type     SMALLINT,   

    co_applicant_credit_score_type  SMALLINT,
    denial_reason_1                 SMALLINT,
    loan_to_value_ratio             DECIMAL (18,4),
    income                          DECIMAL (18,4),
    debt_to_income_ratio            DECIMAL (16,4), 
    derived_loan_product_type       TEXT  
);