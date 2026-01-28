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
    application_id                  BIGSERIAL PRIMARY KEY, -- auto gen
    preapproval                     SMALLINT,
    applicant_credit_score_type     SMALLINT,     
    co_applicant_credit_score_type  SMALLINT,
    derived_loan_product_type       TEXT,
    loan_purpose                    SMALLINT,  

    created_at                      TIMESTAMPTZ DEFAULT now() -- records when borrower is entered into system
);

-- accepted table
CREATE TABLE Accepted_Loans (
    application_id                  BIGINT NOT NULL REFERENCES borrowers(application_id),
    income                          NUMERIC(12,2),
    dti                             NUMERIC(12,2),
    loan_to_value_ratio             NUMERIC(10,2),
    loan_amount                     NUMERIC(12,2),
    term_months                     NUMERIC(6,0)
);

-- rejected table 
CREATE TABLE Rejected ( 
    application_id                  BIGINT NOT NULL REFERENCES borrowers(application_id),
    income                          NUMERIC(12,2),
    dti                             NUMERIC(12,2),
    loan_to_value_ratio             NUMERIC(10,2), 
    loan_amount                     NUMERIC(12,2),
    term_months                     NUMERIC(6,0),
    denial_reason_1                 SMALLINT
);

-- ml table?