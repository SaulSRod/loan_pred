from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from ETL.transformation.staging_loader import (
    load_hdma_staging
)

from ETL.transformation.validation_loader import (
    create_valid_accepted_hdma,
    create_valid_rejected_hdma,
    confirm_lengths
)

from ETL.load.transf_loader import (
    run_transf_loader
)

def create_databases() -> None:
    sql_files = [
        "database/database.sql",
        #"database/indexing.sql",
        "database/staging.sql"
    ]

    engine = create_engine("postgresql+psycopg2:///credit_risk")
    
    with engine.begin() as conn:
        for path in sql_files:
            print(f"=== Creating SQL file: {path} ===")
            with open(path, 'r') as f:
                sql = f.read()
            conn.execute(text(sql))

    print("=== Completed database creation ===")

if __name__ == "__main__":
    engine = create_engine("postgresql+psycopg2:///credit_risk")
    try:
        create_databases()
    except Exception as e:
        print(f"Could not create database: {e}")

    try:
        print("=== Loading HDMA staging tables ===")
        load_hdma_staging(sample=False, engine=engine)

        print("=== All staging tables populated ===")
    except Exception as e:
        print(f"Error when trying to execute staging_loader.py: {e}")

    try:
        print("=== Loading VALID HDMA accepted table ===")
        create_valid_accepted_hdma(engine)

        print("=== Loading VALID HDMA rejected table ===")
        create_valid_rejected_hdma(engine)

        print("=== ALL VALID TABLES WERE LOADED ===")
        confirm_lengths(engine)

    except Exception as e:
        print(f"Error when trying to execute validation_loader.py: {e}")

    try:
        run_transf_loader(engine)
    except Exception as e:
        print(f"Error when trying to execute transf_loader.py: {e}")
    