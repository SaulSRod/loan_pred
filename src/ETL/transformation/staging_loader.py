#populate staging tables
# python -m ETL.transformation.staging_loader (run ONCE)

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import pandas as pd
from typing import Optional, Dict
import io
import psycopg2

from ETL.ingestion.data_ingestion_hdma import (
    clean_hdma_accepted,
    clean_hdma_rejected,
)

#helpers -----------
#ret num of rows
def faster_to_sql(df_name: str, engine: Engine, df: pd.DataFrame, table_name: str, columns: list):
    """
    Helper that writes df to memory and then writes to sql database
    """
    try:
        #write df to memory
        output = io.StringIO()
        df.to_csv(output, sep=',', header=False, index=False)
        output.seek(0)

        conn = engine.raw_connection()
        cursor = conn.cursor()

        print(f"[staging_loader] writing {df_name} to {table_name} using STRINGIO")
        cursor.copy_from(output, table = "staging_accepted_hdma", sep = ",", null = "", columns = columns)
        conn.commit()
        cursor.close()
        conn.close()
        """
        #first_line = output.readline()
        #print(first_line)
        #output.seek(0)
        """
        return len(df)

    except Exception as e:
        print(f"Error in staging_loader.py -> write_df_to_table: {e}")

# load staging hdma table faster by using memory instead of df.to_sql-------------
def load_hdma_staging(sample: bool = True,seed: int = 0,engine: Optional[Engine] = None,) -> None:
    """
    Function that writes dataframe to memory and avoids using df.to_sql
    > Given that df.to_sql writes using single queries to database, time quickly adds up even when using chunksize.
    > Chunksize showed minimal time reduction given our files are 3 MIL and 2.3MIL rows.
    > STRINGIO reduces load time from minutes to seconds.
    """
    if engine is None:
        engine = create_engine("postgresql+psycopg2:///credit_risk")

    accepted_df = clean_hdma_accepted(sample=sample,seed=seed,)
    rejected_df = clean_hdma_rejected(sample=sample,seed=seed,)

    print(f"[staging_loader] HDMA accepted rows: {len(accepted_df)}")
    print(f"[staging_loader] HDMA rejected rows: {len(rejected_df)}")

    #load accepted data
    accepted_cols = ['activity_year', 'action_taken', 'preapproval', 'loan_purpose', 'loan_amount', 'loan_term', 'applicant_credit_score_type',
        'co_applicant_credit_score_type' , 'loan_to_value_ratio', 'income', 'debt_to_income_ratio', 'derived_loan_product_type']
    
    accepted_stage = accepted_df[accepted_cols].copy()

    #load accepted df to sql table using memory
    try:
        inserted_acc = faster_to_sql(df_name = "HDMA_accepted", engine = engine, df = accepted_stage, table_name = "staging_accepted_hdma", columns = accepted_cols)
        print(f"[staging_loader] Inserted {inserted_acc} rows inside staging_accepted_hdma")
    except Exception as e:
        print(f"Error in staging_loader.py -> write_df_to_table: {e}")

    #load rejected data
    rejected_cols = ['activity_year', 'action_taken', 'preapproval', 'loan_purpose', 'loan_amount', 'loan_term', 'applicant_credit_score_type',
        'co_applicant_credit_score_type', 'denial_reason_1', 'loan_to_value_ratio', 'income', 'debt_to_income_ratio', 'derived_loan_product_type']
    rejected_stage = rejected_df[rejected_cols].copy()
    try:
        print("writing df to sql table -> staging_rejected_hdma")
        inserted_rejec = faster_to_sql("HDMA_rejected", engine = engine, df = rejected_stage, table_name="staging_rejected_hdma", columns= rejected_cols)
        print(f"[staging_loader] Inserted {inserted_rejec} rows inside staging_rejected_hdma")
    except Exception as e:
        print(f"Error in staging_loader.py -> write_df_to_table: {e}")

if __name__ == "__main__":
    engine = create_engine("postgresql+psycopg2:///credit_risk", executemany_mode="values_plus_batch", insertmanyvalues_page_size=100000, executemany_batch_page_size=100000)

    print("=== Loading HDMA staging tables ===")
    
    load_hdma_staging(sample = False, engine = engine)
    
    print("=== HDMA staging table populated ===")

    ''' 
    '''