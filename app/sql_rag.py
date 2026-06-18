from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import Settings, get_settings
from app.generation.llm import build_llm


SQL_PROMPT = ChatPromptTemplate.from_template(
    """You convert business questions into safe SQLite SELECT queries.

Database schema:
claims(claim_id, patient_id, patient_name, department, claim_type, diagnosis_code, insurer, claimed_amount, approved_amount, status, submitted_date, resolved_date)
maintenance_tickets(ticket_id, equipment_name, equipment_id, category, campus, issue_type, fault_code, raised_by, raised_date, resolved_date, status, resolution_note)

Rules:
- Return one SQLite SELECT statement only.
- Do not use INSERT, UPDATE, DELETE, DROP, ALTER, PRAGMA, or ATTACH.
- Use only the listed tables and columns.
- Add a LIMIT 25 unless the query uses aggregate functions.

Question: {question}
SQL:"""
)

SQL_ANSWER_PROMPT = ChatPromptTemplate.from_template(
    """You are MediBot. Answer the question using only this SQL result.

Question: {question}
SQL: {sql}
Rows: {rows}

Give a concise plain-text answer. If there are no rows, say no matching records were found.
Answer:"""
)


def should_use_sql_rag(question: str) -> bool:
    text = question.lower()
    keywords = [
        "claim",
        "claims",
        "approved amount",
        "claimed amount",
        "insurer",
        "maintenance",
        "ticket",
        "tickets",
        "equipment id",
        "fault code",
        "status",
        "how many",
        "count",
        "average",
        "total",
        "highest",
        "lowest",
    ]
    return any(keyword in text for keyword in keywords)


def _clean_sql(raw_sql: str) -> str:
    sql = raw_sql.strip()
    fenced = re.search(r"```(?:sql)?\s*(.*?)```", sql, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        sql = fenced.group(1).strip()

    match = re.search(r"\bselect\b.*", sql, flags=re.IGNORECASE | re.DOTALL)
    if match:
        sql = match.group(0).strip()

    sql = sql.rstrip(";")
    if not re.match(r"^select\b", sql, flags=re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed for SQL RAG.")

    blocked = r"\b(insert|update|delete|drop|alter|pragma|attach|detach|replace|create)\b"
    if re.search(blocked, sql, flags=re.IGNORECASE):
        raise ValueError("Unsafe SQL generated.")

    return sql


def _execute_sql(db_path: Path, sql: str) -> list[dict[str, object]]:
    if not db_path.exists():
        raise FileNotFoundError(f"SQLite database not found: {db_path}")

    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(sql).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


class SQLRAG:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.llm = build_llm(self.settings)
        self.sql_chain = SQL_PROMPT | self.llm | StrOutputParser()
        self.answer_chain = SQL_ANSWER_PROMPT | self.llm | StrOutputParser()

    def ask(self, question: str) -> dict[str, object]:
        raw_sql = self.sql_chain.invoke({"question": question})
        sql = _clean_sql(raw_sql)
        rows = _execute_sql(self.settings.sqlite_db_path, sql)
        answer = self.answer_chain.invoke({"question": question, "sql": sql, "rows": rows})
        return {
            "answer": answer.strip(),
            "sql": sql,
            "rows": rows,
            "sources": [{"source_document": self.settings.sqlite_db_path.name, "collection": "db"}],
        }


def sql_rag_chain(question: str) -> str:
    return SQLRAG().ask(question)["answer"]
