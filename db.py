import os
import urllib.parse
from sqlalchemy import create_engine, text
import streamlit as st

# Monta a connection string priorizando secrets do Streamlit
def _conn_params():
    if "sqlserver" in st.secrets:
        cfg = st.secrets["sqlserver"]
        return {
            "DRIVER": cfg.get("driver", "ODBC Driver 18 for SQL Server"),
            "SERVER": f"{cfg.get('host','localhost')},{cfg.get('port',1433)}",
            "DATABASE": cfg.get("database", "SalesDB"),
            "UID": cfg.get("user", "sa"),
            "PWD": cfg.get("password", "SenhaForte123"),
            "Encrypt": "yes",
            "TrustServerCertificate": "yes" if cfg.get("trust_server_certificate", True) else "no",
        }
    # fallback via env
    return {
        "DRIVER": os.getenv("SQLSERVER_DRIVER", "ODBC Driver 18 for SQL Server"),
        "SERVER": f"{os.getenv('SQLSERVER_HOST','localhost')},{os.getenv('SQLSERVER_PORT','1433')}",
        "DATABASE": os.getenv("SQLSERVER_DB", "SalesDB"),
        "UID": os.getenv("SQLSERVER_USER", "sa"),
        "PWD": os.getenv("SQLSERVER_PASSWORD", "SenhaForte123"),
        "Encrypt": "yes",
        "TrustServerCertificate": "yes",
    }

def _odbc_str(params: dict) -> str:
    # String ODBC com Encrypt e TrustServerCertificate (necessário no Driver 18)
    return (
        f"DRIVER={{{params['DRIVER']}}};"
        f"SERVER={params['SERVER']};"
        f"DATABASE={params['DATABASE']};"
        f"UID={params['UID']};PWD={params['PWD']};"
        f"Encrypt={params['Encrypt']};"
        f"TrustServerCertificate={params['TrustServerCertificate']};"
    )

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        params = _conn_params()
        odbc_str = _odbc_str(params)
        conn_url = f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(odbc_str)}"
        _engine = create_engine(conn_url, pool_pre_ping=True, fast_executemany=True)
    return _engine

def run_query(sql: str, params: dict):
    """
    Executa SQL parametrizado com SQLAlchemy.
    Retorna lista de dicts (mappings), ideal para criar um DataFrame.
    """
    eng = get_engine()
    with eng.connect() as conn:
        return conn.execute(text(sql), params).mappings().all()
