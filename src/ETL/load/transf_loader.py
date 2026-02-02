#python -m ETL.load.transf_loader

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.engine import Engine

from ETL.load.mapping.borrowers_map import map_all_borrowers
from ETL.load.mapping.rejected_map import map_all_rejected_loans

def confirm_lengths(engine: Engine) -> None:
    queries = {
        "borrowers": "SELECT COUNT(*) FROM borrowers;",
        "rejected": "SELECT COUNT(*) FROM rejected",
    }

    with engine.connect() as conn:
        for name, query in queries.items():
            result = conn.execute(text(query)).scalar()
            print(f"{name} size -> {result}")

def run_transf_loader(engine: Engine | None = None) -> None:
    if engine is None:
        engine = create_engine("postgresql+psycopg2:///credit_risk")

    print("=== Mapping into Borrowers ===")
    map_all_borrowers(engine)

    print("=== Mapping into Rejected ===")
    map_all_rejected_loans(engine)

    #from ETL.load.mapping.accepted_loans_map import map_all_accepted_loans
    #print("=== Mapping into Accepted_Loans ===")
    #map_all_accepted_loans(engine)

    confirm_lengths(engine)

    print("=== transf_loader SUCCESS!! ===")

if __name__ == "__main__":
    engine = create_engine("postgresql+psycopg2:///credit_risk")
    run_transf_loader(engine)
