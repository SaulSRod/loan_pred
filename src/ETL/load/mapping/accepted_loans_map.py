from sqlalchemy import text
from sqlalchemy.engine import Engine

def map_accepted_loans_from_hdma(engine: Engine) -> None:
    """
    Maps the accepted loans from hdma into SQL table
        loan_amount      -> loan_amnt
        loan_term        -> term_months
        interest_rate    -> int_rate
    """

    sql = text(
        """
        WITH cleaned_hdma AS (
            SELECT
                sh.*,
                NULLIF(REGEXP_REPLACE(sh.debt_to_income_ratio, '[^0-9\\.]', '', 'g'),'')::NUMERIC(6,2) AS dti_clean,
                NULLIF(REGEXP_REPLACE(CAST(sh.loan_amount AS TEXT), '[^0-9\\.]', '', 'g'),'')::NUMERIC(12,2) AS loan_amnt_clean
            FROM valid_accepted_hdma sh
        ),
        hdma_with_borrower AS (
            SELECT
                ch.*,
                b.borrower_id
            FROM cleaned_hdma ch
            JOIN Borrowers b
              ON b.income                       = ch.income
             AND b.debt_to_income_ratio         = ch.dti_clean
             AND b.applicant_credit_score_type  = ch.applicant_credit_score_type
             AND b.co_applicant_credit_score_type = ch.co_applicant_credit_score_type
        ),
        numbered AS (
            SELECT
                hw.*,
                (
                    SELECT COALESCE(MAX(al.loan_id), 0)
                    FROM Accepted_Loans al
                ) + ROW_NUMBER() OVER (
                    ORDER BY hw.activity_year, hw.loan_amnt_clean, hw.income
                ) AS new_loan_id
            FROM hdma_with_borrower hw
        )
        INSERT INTO Accepted_Loans (
            loan_id,
            borrower_id,
            loan_amnt,
            funded_amnt,
            term_months,
            int_rate,
            installment,
            income,
            dti,
            loan_status,
            purpose,
            application_type,
            activity_year,
            action_taken,
            preapproval,
            loan_to_value_ratio,
            total_loan_costs,
            derived_loan_product_type,
            loan_purpose
        )
        SELECT
            n.new_loan_id               AS loan_id,
            n.borrower_id,
            n.loan_amnt_clean           AS loan_amnt,
            NULL::NUMERIC(12,2)         AS funded_amnt,
            n.loan_term                 AS term_months,
            n.interest_rate             AS int_rate,
            NULL::NUMERIC(12,2)         AS installment,
            n.income                    AS income,
            n.dti_clean                 AS dti,
            NULL::VARCHAR(40)           AS loan_status,
            NULL::VARCHAR(50)           AS purpose,
            NULL::VARCHAR(30)           AS application_type,
            n.activity_year,
            n.action_taken,
            n.preapproval,
            n.loan_to_value_ratio,
            n.total_loan_costs,
            n.derived_loan_product_type,
            n.loan_purpose
        FROM numbered n;
        """
    )

    with engine.begin() as conn:
        conn.execute(sql)

def map_all_accepted_loans(engine: Engine) -> None:
    map_accepted_loans_from_hdma(engine)
