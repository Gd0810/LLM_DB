import os
import re
import json
from typing import Any, Dict, List, Optional

import requests
import mysql.connector
from mysql.connector import Error


class NvidiaLLMClient:
    def __init__(
        self,
        api_key: str,
        api_url: str,
        model: str = "gpt-35-turbo",
        temperature: float = 0.0,
    ):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.temperature = temperature

    @classmethod
    def from_env(cls) -> "NvidiaLLMClient":
        api_key = os.getenv("NVIDIA_API_KEY", "")
        api_url = os.getenv("NVIDIA_API_URL", "")
        model = os.getenv("NVIDIA_MODEL", "gpt-35-turbo")
        if not api_key:
            raise ValueError("Missing NVIDIA_API_KEY environment variable.")
        if not api_url:
            raise ValueError("Missing NVIDIA_API_URL environment variable.")
        return cls(api_key=api_key, api_url=api_url, model=model)

    def complete(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "input": prompt,
            "temperature": self.temperature,
            "max_output_tokens": 1024,
        }

        response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        body = response.json()
        return self._parse_response(body)

    @staticmethod
    def _parse_response(body: Dict[str, Any]) -> str:
        if isinstance(body, dict):
            if "choices" in body and body["choices"]:
                first = body["choices"][0]
                if isinstance(first, dict):
                    if "text" in first:
                        return first["text"]
                    if "message" in first and isinstance(first["message"], dict):
                        return first["message"].get("content", "")
            if "outputs" in body and body["outputs"]:
                output = body["outputs"][0]
                if isinstance(output, dict):
                    if "content" in output:
                        content = output["content"]
                        if isinstance(content, list) and content:
                            first = content[0]
                            if isinstance(first, dict):
                                return first.get("text", "")
                            if isinstance(first, str):
                                return first
                    if "text" in output:
                        return output["text"]
        raise ValueError("Unable to parse NVIDIA LLM response. Received: %s" % json.dumps(body))


class DatabaseChatbot:
    def __init__(
        self,
        mysql_host: str,
        mysql_port: int,
        mysql_user: str,
        mysql_password: str,
        mysql_database: str,
        llm_client: NvidiaLLMClient,
    ):
        self.mysql_database = mysql_database
        self.llm_client = llm_client
        self.connection = self._connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database,
        )
        self.schema_description = self._load_schema_description()

    @classmethod
    def from_env(cls) -> "DatabaseChatbot":
        mysql_host = os.getenv("MYSQL_HOST", "localhost")
        mysql_port = int(os.getenv("MYSQL_PORT", "3306"))
        mysql_user = os.getenv("MYSQL_USER", "root")
        mysql_password = os.getenv("MYSQL_PASSWORD", "")
        mysql_database = os.getenv("MYSQL_DATABASE", "product_demo_db")
        llm_client = NvidiaLLMClient.from_env()
        return cls(
            mysql_host=mysql_host,
            mysql_port=mysql_port,
            mysql_user=mysql_user,
            mysql_password=mysql_password,
            mysql_database=mysql_database,
            llm_client=llm_client,
        )

    def _connect(self, host: str, port: int, user: str, password: str, database: str):
        try:
            connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
            )
            if not connection.is_connected():
                raise ConnectionError("Failed to connect to the MySQL database.")
            return connection
        except Error as error:
            raise ConnectionError(f"MySQL connection failed: {error}") from error

    def _load_schema_description(self) -> str:
        table_definitions: List[str] = []
        foreign_keys: List[str] = []

        with self.connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall() or []]

            for table in tables:
                cursor.execute(f"SHOW COLUMNS FROM `{table}`")
                columns = [f"{column[0]} {column[1]}" for column in cursor.fetchall() or []]
                table_definitions.append(f"{table}: {', '.join(columns)}")

            cursor.execute(
                "SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME "
                "FROM information_schema.key_column_usage "
                "WHERE TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME IS NOT NULL",
                (self.mysql_database,),
            )
            for row in cursor.fetchall() or []:
                table_definitions.append(
                    f"Foreign key: {row[0]}.{row[1]} -> {row[2]}.{row[3]}"
                )

        return "\n".join(table_definitions)

    def _build_prompt(self, question: str) -> str:
        prompt = (
            "You are a read-only database assistant for a MySQL database. "
            "Use only the tables and columns available in the schema below. "
            "Return a single SQL SELECT query that answers the user question. "
            "Do not use INSERT, UPDATE, DELETE, DROP, CREATE, or any schema changes. "
            "Use standard MySQL syntax and prefer simple joins when needed. "
            "Output only the SQL query itself, without explanation or analysis.\n\n"
            f"Database name: {self.mysql_database}\n"
            "Schema:\n"
            f"{self.schema_description}\n\n"
            f"Question: {question}\n"
            "SQL_QUERY:"
        )
        return prompt

    @staticmethod
    def _extract_sql(text: str) -> Optional[str]:
        pattern = re.compile(r"(?si)(SELECT\b.*?)(?:;|$)")
        match = pattern.search(text.strip())
        if not match:
            return None
        sql = match.group(1).strip()
        return sql

    def _execute_sql(self, sql: str) -> List[Dict[str, Any]]:
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
        return rows

    @staticmethod
    def _format_results(rows: List[Dict[str, Any]]) -> str:
        if not rows:
            return "No results found for that query."
        return json.dumps(rows, indent=2, default=str)

    def answer_question(self, question: str) -> str:
        prompt = self._build_prompt(question)
        model_output = self.llm_client.complete(prompt)

        sql = self._extract_sql(model_output)
        if not sql:
            raise ValueError(
                "The NVIDIA LLM response did not contain a valid SELECT query. "
                "You can inspect the raw response for debugging."
            )

        rows = self._execute_sql(sql)
        result_text = self._format_results(rows)
        return f"SQL QUERY:\n{sql}\n\nRESULTS:\n{result_text}"

    def close(self) -> None:
        if self.connection.is_connected():
            self.connection.close()
