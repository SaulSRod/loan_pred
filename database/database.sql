-- psql -d postgres
-- CREATE DATABASE credit_risk;
-- \l -- to verify u created it
-- \q -- to exit

-- psql -d credit_risk
-- \dt -- list all tables
-- \d borrowers -- peek inside borrowers table

-- psql -d credit_risk -f database/database.sql

DROP TABLE IF EXISTS Borrowers CASCADE;
DROP TABLE IF EXISTS Accepted_Loans CASCADE;
DROP TABLE IF EXISTS Rejected CASCADE;

-- customers table
CREATE TABLE Borrowers (
    borrower_id                     BIGSERIAL PRIMARY KEY, -- auto gen
    action_taken                    SMALLINT,
    preapproval                     SMALLINT,
    loan_purpose                    SMALLINT,
    derived_loan_product_type       TEXT

    created_at                      TIMESTAMPTZ DEFAULT now() -- records when borrower is entered into system
);

-- accepted table
CREATE TABLE Accepted_Loans (
    --PK
    accepted_id                     BIGSERIAL PRIMARY KEY,
    --FK
    borrower_id                     INTEGER NOT NULL REFERENCES borrowers(application_id),
    
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

-- rejected table 
CREATE TABLE Rejected ( 
    --PK
    rejection_id                    BIGSERIAL PRIMARY KEY,
    --FK
    borrower_id                     INTEGER NOT NULL REFERENCES borrowers(application_id),

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

-- ml table?