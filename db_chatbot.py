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
        base_url = os.getenv("NVIDIA_BASE_URL", "").strip()
        api_url = os.getenv("NVIDIA_API_URL", "").strip()
        model = os.getenv("NVIDIA_MODEL", "openai/gpt-oss-120b")

        if not api_key:
            raise ValueError("Missing NVIDIA_API_KEY environment variable.")

        if base_url:
            api_url = base_url
        if not api_url:
            raise ValueError(
                "Missing NVIDIA_BASE_URL or NVIDIA_API_URL environment variable."
            )

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

        api_url = self.api_url.rstrip("/")
        if api_url.endswith("/v1"):
            api_url = api_url + "/responses"

        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        if response.status_code == 401:
            raise ValueError(
                "Unauthorized: NVIDIA API key was rejected. "
                "Check NVIDIA_API_KEY, NVIDIA_BASE_URL, and NVIDIA_MODEL in your .env file."
            )
        if response.status_code == 403:
            raise ValueError(
                "Forbidden: NVIDIA API key does not have access to the requested model or endpoint. "
                "Verify your key permissions and model name."
            )
        response.raise_for_status()

        body = response.json()
        return self._parse_response(body)

    @staticmethod
    def _extract_text(value: Any) -> Optional[str]:
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            if value.get("type") in {"output_text", "message"} and "text" in value:
                return str(value["text"])
            for key in ("text", "content", "message"):
                if key in value:
                    extracted = NvidiaLLMClient._extract_text(value[key])
                    if extracted:
                        return extracted
        if isinstance(value, list):
            for item in value:
                extracted = NvidiaLLMClient._extract_text(item)
                if extracted:
                    return extracted
        return None

    @staticmethod
    def _extract_output_text(entry: Any) -> Optional[str]:
        if isinstance(entry, dict):
            if entry.get("type") == "reasoning":
                return None
            if "content" in entry:
                content = entry["content"]
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "output_text":
                            text = NvidiaLLMClient._extract_text(item)
                            if text:
                                return text
                    for item in content:
                        text = NvidiaLLMClient._extract_text(item)
                        if text:
                            return text
                else:
                    text = NvidiaLLMClient._extract_text(content)
                    if text:
                        return text
            if entry.get("role") == "assistant" and "content" in entry:
                return NvidiaLLMClient._extract_text(entry["content"])
        return NvidiaLLMClient._extract_text(entry)

    @staticmethod
    def _parse_response(body: Dict[str, Any]) -> str:
        if isinstance(body, dict):
            if "choices" in body and body["choices"]:
                first = body["choices"][0]
                if isinstance(first, dict):
                    text = NvidiaLLMClient._extract_output_text(first)
                    if text:
                        return text
            for key in ("outputs", "output"):
                if key in body and body[key]:
                    entries = body[key]
                    if isinstance(entries, list):
                        for entry in entries:
                            text = NvidiaLLMClient._extract_output_text(entry)
                            if text:
                                return text
                    else:
                        text = NvidiaLLMClient._extract_output_text(entries)
                        if text:
                            return text
            text = NvidiaLLMClient._extract_text(body)
            if text:
                return text
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

        table_definitions.append(
            "Relationships: product.category_id = product_category.category_id; "
            "product_sales.product_id = product.product_id"
        )
        return "\n".join(table_definitions)

    def _build_prompt(self, question: str) -> str:
        prompt = (
            "You are a read-only database assistant for a MySQL database. "
            "Use only the tables and columns available in the schema below. "
            "Return a single SQL SELECT query that answers the user question. "
            "Do not use INSERT, UPDATE, DELETE, DROP, CREATE, or any schema changes. "
            "Use standard MySQL syntax and prefer simple joins when needed. "
            "Output only the SQL query itself, without explanation or analysis. "
            "If the question is not a database query, do not return SQL.\n\n"
            "Example queries:\n"
            "- List all products: SELECT * FROM product\n"
            "- Products by category: SELECT p.product_name, c.category_name FROM product p JOIN product_category c ON p.category_id = c.category_id\n"
            "- Sales data: SELECT * FROM product_sales\n"
            "- Products with sales: SELECT p.product_name, s.quantity_sold, s.sale_date FROM product p JOIN product_sales s ON p.product_id = s.product_id\n\n"
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
    def _is_greeting(question: str) -> bool:
        normalized = question.strip().lower()
        return bool(
            re.fullmatch(
                r"(hi|hello|hey|hey there|good morning|good afternoon|good evening|how are you|what's up|whats up)[.!]?",
                normalized,
            )
        )

    @staticmethod
    def _extract_category_from_question(question: str) -> Optional[str]:
        normalized = question.lower()
        patterns = [
            r"([a-z0-9 ]+) category",
            r"category ([a-z0-9 ]+)",
            r"books",
        ]
        for pattern in patterns:
            match = re.search(pattern, normalized)
            if match:
                category_name = match.group(1).strip() if match.groups() else match.group(0).strip()
                return category_name.title()
        return None

    @staticmethod
    def _format_results(rows: List[Dict[str, Any]], question: str) -> str:
        if not rows:
            category_name = DatabaseChatbot._extract_category_from_question(question)
            if category_name:
                return f"No products found in the {category_name} category."
            if "sale" in question.lower():
                return "No sales records found for that query."
            return "No, I could not find any matching records."

        if len(rows) == 1:
            row = rows[0]
            product_name = row.get("product_name") or row.get("name")
            category_name = row.get("category_name")
            price = row.get("product_price") or row.get("price")
            quantity = row.get("product_count") or row.get("quantity") or row.get("stock")
            quantity_sold = row.get("quantity_sold")
            sale_date = row.get("sale_date")

            if product_name:
                parts = []
                if category_name:
                    parts.append(f"in {category_name} category")
                if price is not None:
                    parts.append(f"price is {price}")
                if quantity is not None:
                    parts.append(f"quantity is {quantity}")
                if quantity_sold is not None:
                    parts.append(f"sold {quantity_sold}")
                if sale_date:
                    parts.append(f"sold on {sale_date}")

                if parts:
                    return f"Yes, I have {product_name}. {' '.join(parts)}."
                return f"Yes, I have {product_name}."

            # For non-product queries, show key fields
            field_text = []
            for key, value in row.items():
                if key not in ['id', 'category_id', 'product_id']:
                    field_text.append(f"{key.replace('_', ' ')} {value}")
            if field_text:
                return "Found one record: " + ", ".join(field_text) + "."

        # Multiple records
        sample_info = []
        for row in rows[:5]:
            info_parts = []
            product_name = row.get("product_name") or row.get("name")
            category_name = row.get("category_name")
            price = row.get("product_price") or row.get("price")

            if product_name:
                info_parts.append(product_name)
            if category_name:
                info_parts.append(f"({category_name})")
            if price is not None:
                info_parts.append(f"₹{price}")

            if info_parts:
                sample_info.append(" ".join(info_parts))
            else:
                # Fallback for other types of records
                key_values = [f"{k}={v}" for k, v in list(row.items())[:3]]
                sample_info.append(", ".join(key_values))

        if sample_info:
            summary = "; ".join(sample_info)
            if len(rows) <= 5:
                return f"Found {len(rows)} matching records: {summary}."
            return f"Found {len(rows)} matching records. Examples: {summary}."

        return f"Found {len(rows)} matching records."

    def answer_question(self, question: str) -> str:
        if self._is_greeting(question):
            return (
                "Hello! I can answer questions about the product_demo_db database. "
                "Ask me about products, categories, or sales."
            )

        prompt = self._build_prompt(question)
        model_output = self.llm_client.complete(prompt)

        sql = self._extract_sql(model_output)
        if not sql:
            raise ValueError(
                "The NVIDIA LLM response did not contain a valid SELECT query. "
                "You can inspect the raw response for debugging."
            )


        rows = self._execute_sql(sql)
        return self._format_results(rows, question)

    def close(self) -> None:
        if self.connection.is_connected():
            self.connection.close()
