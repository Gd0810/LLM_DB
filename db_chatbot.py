import os
import re
import json
from typing import Any, Dict, List, Optional, Tuple

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
    VALID_OPERATIONS = {"read", "create", "update", "delete", "none"}
    VALID_FILTER_OPERATORS = {
        "=",
        "!=",
        ">",
        "<",
        ">=",
        "<=",
        "LIKE",
        "IN",
        "BETWEEN",
        "IS NULL",
        "IS NOT NULL",
    }
    AGGREGATE_FUNCTIONS = {"SUM", "COUNT", "AVG", "MIN", "MAX"}
    SEARCH_STOPWORDS = {
        "a",
        "an",
        "and",
        "any",
        "by",
        "for",
        "from",
        "get",
        "give",
        "in",
        "list",
        "me",
        "of",
        "overall",
        "please",
        "product",
        "products",
        "show",
        "tell",
        "the",
        "to",
        "with",
        "price",
        "amount",
        "category",
        "categories",
    }

    def __init__(
        self,
        mysql_host: str,
        mysql_port: int,
        mysql_user: str,
        mysql_password: str,
        mysql_database: str,
        llm_client: NvidiaLLMClient,
        max_read_rows: int = 200,
    ):
        self.mysql_database = mysql_database
        self.llm_client = llm_client
        self.max_read_rows = max(1, max_read_rows)
        self.connection = self._connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database,
        )
        self.schema = self._load_schema_metadata()
        self.schema_description = self._build_schema_description()

    @classmethod
    def from_env(cls) -> "DatabaseChatbot":
        mysql_host = os.getenv("MYSQL_HOST", "localhost")
        mysql_port = int(os.getenv("MYSQL_PORT", "3306"))
        mysql_user = os.getenv("MYSQL_USER", "root")
        mysql_password = os.getenv("MYSQL_PASSWORD", "")
        mysql_database = os.getenv("MYSQL_DATABASE", "")
        max_read_rows = int(os.getenv("MAX_READ_ROWS", "200"))

        if not mysql_database.strip():
            raise ValueError("Missing MYSQL_DATABASE environment variable.")

        llm_client = NvidiaLLMClient.from_env()
        return cls(
            mysql_host=mysql_host,
            mysql_port=mysql_port,
            mysql_user=mysql_user,
            mysql_password=mysql_password,
            mysql_database=mysql_database,
            llm_client=llm_client,
            max_read_rows=max_read_rows,
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

    def _load_schema_metadata(self) -> Dict[str, Any]:
        schema: Dict[str, Any] = {"tables": {}}

        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """,
                (self.mysql_database,),
            )
            tables = [row["table_name"] for row in cursor.fetchall() or []]

            for table_name in tables:
                cursor.execute(
                    """
                    SELECT column_name, column_type, is_nullable, column_key, extra
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position
                    """,
                    (self.mysql_database, table_name),
                )
                column_rows = cursor.fetchall() or []

                columns: Dict[str, Dict[str, Any]] = {}
                primary_keys: List[str] = []
                for row in column_rows:
                    column_name = row["column_name"]
                    columns[column_name] = {
                        "type": row["column_type"],
                        "nullable": str(row["is_nullable"]).upper() == "YES",
                        "key": row["column_key"],
                        "extra": row["extra"],
                    }
                    if row["column_key"] == "PRI":
                        primary_keys.append(column_name)

                cursor.execute(
                    """
                    SELECT column_name, referenced_table_name, referenced_column_name
                    FROM information_schema.key_column_usage
                    WHERE table_schema = %s
                      AND table_name = %s
                      AND referenced_table_name IS NOT NULL
                    ORDER BY column_name
                    """,
                    (self.mysql_database, table_name),
                )
                foreign_keys = cursor.fetchall() or []

                schema["tables"][table_name] = {
                    "columns": columns,
                    "primary_keys": primary_keys,
                    "foreign_keys": foreign_keys,
                }

        return schema

    def _build_schema_description(self) -> str:
        lines: List[str] = []
        for table_name, table_meta in self.schema["tables"].items():
            column_parts = []
            for col_name, col_meta in table_meta["columns"].items():
                col_desc = f"{col_name} {col_meta['type']}"
                if col_name in table_meta["primary_keys"]:
                    col_desc += " [PK]"
                if col_meta["extra"]:
                    col_desc += f" [{col_meta['extra']}]"
                column_parts.append(col_desc)

            lines.append(f"Table {table_name}: {', '.join(column_parts)}")

            if table_meta["foreign_keys"]:
                fk_parts = []
                for fk in table_meta["foreign_keys"]:
                    fk_parts.append(
                        f"{fk['column_name']} -> {fk['referenced_table_name']}.{fk['referenced_column_name']}"
                    )
                lines.append(f"Foreign keys: {', '.join(fk_parts)}")

        if not lines:
            return "No tables found in the selected database."
        return "\n".join(lines)

    def _build_prompt(self, question: str) -> str:
        return f"""You are a MySQL database action planner. Given the schema and user request, output ONLY a valid JSON object with no markdown.

Allowed operations: read, create, update, delete, none
Rules:
1) Use only tables and columns from the schema.
2) If request is not a database task, return operation=none. Short noun phrases (example: "book", "iphone 14 price") are still database read requests.
3) For read: include optional select, filters, order_by, limit. Aggregate expressions are allowed in select.
4) For create: include values object.
5) For update: include values object and filters array.
6) For delete: include filters array (never empty).
7) Keep limit <= {self.max_read_rows}.
8) Use filter operators only from: =, !=, >, <, >=, <=, LIKE, IN, BETWEEN, IS NULL, IS NOT NULL.

JSON format:
{{
  "operation": "read|create|update|delete|none",
  "table": "table_name_or_empty",
  "select": ["*" or column names or aggregate expressions like "SUM(amount) AS total_amount"],
  "values": {{"column": value}},
  "filters": [{{"column": "col", "operator": "=", "value": 123}}],
  "order_by": [{{"column": "col", "direction": "asc|desc"}}],
  "limit": 25,
  "message": "optional clarification"
}}

Database: {self.mysql_database}
Schema:
{self.schema_description}

User request: {question}
JSON:"""

    @staticmethod
    def _extract_json(text: str) -> Optional[Dict[str, Any]]:
        text = text.strip()

        # Try direct JSON first.
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        # Try fenced block.
        fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
        if fenced_match:
            try:
                parsed = json.loads(fenced_match.group(1))
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass

        # Try the largest object-shaped substring.
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                return None

        return None

    @staticmethod
    def _is_valid_identifier(name: str) -> bool:
        return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name or ""))

    @staticmethod
    def _normalize_operation(value: Any) -> str:
        return str(value or "").strip().lower()

    @staticmethod
    def _is_text_column_type(column_type: str) -> bool:
        normalized = str(column_type or "").lower()
        text_markers = ("char", "text", "enum", "set", "json")
        return any(marker in normalized for marker in text_markers)

    def _extract_search_terms(self, question: str) -> List[str]:
        raw_terms = re.findall(r"[a-z0-9]+", question.lower())
        terms: List[str] = []
        for term in raw_terms:
            if len(term) < 2:
                continue
            if term in self.SEARCH_STOPWORDS:
                continue
            terms.append(term)
        return terms

    def _fallback_read_search(self, question: str, limit: int = 20) -> Optional[Dict[str, Any]]:
        terms = self._extract_search_terms(question)
        if not terms:
            return None

        table_rows: List[Dict[str, Any]] = []
        remaining = min(max(1, limit), self.max_read_rows)

        search_modes = ("AND", "OR")
        with self.connection.cursor(dictionary=True) as cursor:
            for mode in search_modes:
                if remaining <= 0:
                    break

                for table_name, table_meta in self.schema["tables"].items():
                    if remaining <= 0:
                        break

                    text_columns = [
                        column_name
                        for column_name, column_meta in table_meta["columns"].items()
                        if self._is_text_column_type(column_meta.get("type", ""))
                    ]
                    if not text_columns:
                        continue

                    term_clauses: List[str] = []
                    params: List[Any] = []
                    for term in terms:
                        per_term_clauses = []
                        normalized_term = f"%{term.replace(' ', '')}%"
                        for column in text_columns:
                            per_term_clauses.append(
                                f"LOWER(REPLACE(CAST(`{column}` AS CHAR), ' ', '')) LIKE %s"
                            )
                            params.append(normalized_term)

                        connector = " OR "
                        term_clauses.append("(" + connector.join(per_term_clauses) + ")")

                    if not term_clauses:
                        continue

                    where_connector = " AND " if mode == "AND" else " OR "
                    where_sql = where_connector.join(term_clauses)
                    sql = f"SELECT * FROM `{table_name}` WHERE {where_sql} LIMIT %s"
                    query_params = params + [remaining]

                    cursor.execute(sql, query_params)
                    rows = cursor.fetchall() or []
                    for row in rows:
                        row["__table"] = table_name
                    table_rows.extend(rows)
                    remaining = max(0, limit - len(table_rows))

                if table_rows:
                    break

        if not table_rows:
            return None

        return {
            "operation": "read",
            "table": "multi_table_fallback",
            "row_count": len(table_rows),
            "rows": table_rows[:limit],
        }

    def _validate_column_exists(self, table_name: str, column_name: str) -> None:
        if not self._is_valid_identifier(column_name):
            raise ValueError(f"Invalid column name: {column_name}")

        table_meta = self.schema["tables"][table_name]
        if column_name not in table_meta["columns"]:
            raise ValueError(f"Column '{column_name}' does not exist in table '{table_name}'.")

    def _parse_select_item(self, table_name: str, select_item: str) -> Dict[str, str]:
        item = str(select_item or "").strip()
        if not item:
            raise ValueError("select item cannot be empty.")

        if item == "*":
            return {"kind": "all", "sql": "*"}

        if self._is_valid_identifier(item):
            self._validate_column_exists(table_name, item)
            return {"kind": "column", "sql": f"`{item}`", "column": item}

        aggregate_match = re.fullmatch(
            r"(?is)(SUM|COUNT|AVG|MIN|MAX)\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)(?:\s+AS\s+([A-Za-z_][A-Za-z0-9_]*))?",
            item,
        )
        if aggregate_match:
            function_name = aggregate_match.group(1).upper()
            column_name = aggregate_match.group(2)
            alias = aggregate_match.group(3)

            if function_name not in self.AGGREGATE_FUNCTIONS:
                raise ValueError(f"Unsupported aggregate function: {function_name}")

            self._validate_column_exists(table_name, column_name)
            sql = f"{function_name}(`{column_name}`)"
            if alias:
                sql += f" AS `{alias}`"

            return {
                "kind": "aggregate",
                "sql": sql,
                "function": function_name,
                "column": column_name,
                "alias": alias or "",
            }

        raise ValueError(f"Invalid select expression: {item}")

    def _validate_filters(self, table_name: str, filters: Any) -> List[Dict[str, Any]]:
        if filters is None:
            return []
        if not isinstance(filters, list):
            raise ValueError("filters must be a list.")

        validated: List[Dict[str, Any]] = []
        for item in filters:
            if not isinstance(item, dict):
                raise ValueError("Each filter must be an object.")

            column = str(item.get("column", "")).strip()
            operator = str(item.get("operator", "")).strip().upper()

            if not column or not operator:
                raise ValueError("Each filter must include column and operator.")

            self._validate_column_exists(table_name, column)

            if operator not in self.VALID_FILTER_OPERATORS:
                raise ValueError(f"Unsupported filter operator: {operator}")

            value = item.get("value")
            if operator == "IN":
                if not isinstance(value, list) or not value:
                    raise ValueError("IN operator requires a non-empty list value.")
            elif operator == "BETWEEN":
                if not isinstance(value, list) or len(value) != 2:
                    raise ValueError("BETWEEN operator requires value as [start, end].")
            elif operator in {"IS NULL", "IS NOT NULL"}:
                value = None
            elif "value" not in item:
                raise ValueError(f"Operator {operator} requires a value.")

            validated.append({"column": column, "operator": operator, "value": value})

        return validated

    def _validate_values(self, table_name: str, values: Any) -> Dict[str, Any]:
        if not isinstance(values, dict) or not values:
            raise ValueError("values must be a non-empty object.")

        validated: Dict[str, Any] = {}
        for column, value in values.items():
            column_name = str(column).strip()
            self._validate_column_exists(table_name, column_name)
            validated[column_name] = value

        return validated

    def _validate_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        operation = self._normalize_operation(action.get("operation"))
        if operation not in self.VALID_OPERATIONS:
            raise ValueError(f"Unsupported operation: {operation}")

        if operation == "none":
            return {
                "operation": "none",
                "message": str(action.get("message", "This is not a database action request.")).strip(),
            }

        table_name = str(action.get("table", "")).strip()
        if not table_name:
            raise ValueError("table is required.")
        if not self._is_valid_identifier(table_name):
            raise ValueError(f"Invalid table name: {table_name}")
        if table_name not in self.schema["tables"]:
            raise ValueError(f"Table '{table_name}' does not exist in database '{self.mysql_database}'.")

        validated: Dict[str, Any] = {
            "operation": operation,
            "table": table_name,
            "message": str(action.get("message", "")).strip(),
        }

        if operation == "read":
            select_columns = action.get("select") or ["*"]
            if isinstance(select_columns, str):
                select_columns = [select_columns]
            if not isinstance(select_columns, list) or not select_columns:
                raise ValueError("select must be a non-empty list.")

            normalized_select = [str(col).strip() for col in select_columns]
            if "*" in normalized_select and len(normalized_select) > 1:
                raise ValueError("select cannot combine '*' with named columns.")
            validated["select"] = [
                self._parse_select_item(table_name, select_item)
                for select_item in normalized_select
            ]

            validated["filters"] = self._validate_filters(table_name, action.get("filters"))

            order_by_input = action.get("order_by") or []
            if not isinstance(order_by_input, list):
                raise ValueError("order_by must be a list.")
            order_by: List[Dict[str, str]] = []
            for item in order_by_input:
                if not isinstance(item, dict):
                    raise ValueError("Each order_by item must be an object.")
                column = str(item.get("column", "")).strip()
                direction = str(item.get("direction", "asc")).strip().lower()
                if direction not in {"asc", "desc"}:
                    raise ValueError("order_by direction must be 'asc' or 'desc'.")
                self._validate_column_exists(table_name, column)
                order_by.append({"column": column, "direction": direction})
            validated["order_by"] = order_by

            try:
                limit = int(action.get("limit", 25))
            except (TypeError, ValueError) as error:
                raise ValueError("limit must be a valid integer.") from error

            validated["limit"] = min(max(1, limit), self.max_read_rows)

        elif operation == "create":
            validated["values"] = self._validate_values(table_name, action.get("values"))

        elif operation == "update":
            validated["values"] = self._validate_values(table_name, action.get("values"))
            validated["filters"] = self._validate_filters(table_name, action.get("filters"))
            if not validated["filters"]:
                raise ValueError("update operation requires at least one filter.")

        elif operation == "delete":
            validated["filters"] = self._validate_filters(table_name, action.get("filters"))
            if not validated["filters"]:
                raise ValueError("delete operation requires at least one filter.")

        return validated

    @staticmethod
    def _build_where_clause(filters: List[Dict[str, Any]]) -> Tuple[str, List[Any]]:
        if not filters:
            return "", []

        clauses: List[str] = []
        params: List[Any] = []

        for item in filters:
            column = item["column"]
            operator = item["operator"]
            value = item.get("value")

            if operator == "IN":
                placeholders = ", ".join(["%s"] * len(value))
                clauses.append(f"`{column}` IN ({placeholders})")
                params.extend(value)
            elif operator == "BETWEEN":
                clauses.append(f"`{column}` BETWEEN %s AND %s")
                params.extend(value)
            elif operator in {"IS NULL", "IS NOT NULL"}:
                clauses.append(f"`{column}` {operator}")
            else:
                clauses.append(f"`{column}` {operator} %s")
                params.append(value)

        return " WHERE " + " AND ".join(clauses), params

    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        operation = action["operation"]

        if operation == "none":
            return {
                "operation": "none",
                "message": action.get("message") or "This does not require a database operation.",
            }

        table = action["table"]

        try:
            with self.connection.cursor(dictionary=True) as cursor:
                if operation == "read":
                    select_items = action["select"]
                    select_sql = ", ".join(item["sql"] for item in select_items)

                    where_sql, where_params = self._build_where_clause(action["filters"])

                    sql = f"SELECT {select_sql} FROM `{table}`{where_sql}"

                    if action["order_by"]:
                        order_parts = [
                            f"`{item['column']}` {item['direction'].upper()}"
                            for item in action["order_by"]
                        ]
                        sql += " ORDER BY " + ", ".join(order_parts)

                    sql += " LIMIT %s"
                    params = where_params + [action["limit"]]

                    cursor.execute(sql, params)
                    rows = cursor.fetchall() or []
                    return {
                        "operation": "read",
                        "table": table,
                        "row_count": len(rows),
                        "rows": rows,
                    }

                if operation == "create":
                    values = action["values"]
                    columns = list(values.keys())
                    column_sql = ", ".join(f"`{column}`" for column in columns)
                    placeholders = ", ".join(["%s"] * len(columns))
                    params = [values[column] for column in columns]

                    sql = f"INSERT INTO `{table}` ({column_sql}) VALUES ({placeholders})"
                    cursor.execute(sql, params)
                    self.connection.commit()

                    return {
                        "operation": "create",
                        "table": table,
                        "affected_rows": cursor.rowcount,
                        "last_insert_id": cursor.lastrowid,
                    }

                if operation == "update":
                    values = action["values"]
                    set_columns = list(values.keys())
                    set_sql = ", ".join(f"`{column}` = %s" for column in set_columns)
                    set_params = [values[column] for column in set_columns]

                    where_sql, where_params = self._build_where_clause(action["filters"])
                    sql = f"UPDATE `{table}` SET {set_sql}{where_sql}"
                    params = set_params + where_params

                    cursor.execute(sql, params)
                    self.connection.commit()

                    return {
                        "operation": "update",
                        "table": table,
                        "affected_rows": cursor.rowcount,
                    }

                if operation == "delete":
                    where_sql, where_params = self._build_where_clause(action["filters"])
                    sql = f"DELETE FROM `{table}`{where_sql}"

                    cursor.execute(sql, where_params)
                    self.connection.commit()

                    return {
                        "operation": "delete",
                        "table": table,
                        "affected_rows": cursor.rowcount,
                    }

                raise ValueError(f"Unsupported operation at execution time: {operation}")

        except Error as error:
            self.connection.rollback()
            raise ValueError(f"Database execution failed: {error}") from error

    @staticmethod
    def _is_greeting(question: str) -> bool:
        normalized = question.strip().lower()
        return bool(
            re.fullmatch(
                r"(hi|hello|hey|hey there|good morning|good afternoon|good evening|how are you|what's up|whats up)[.!]?",
                normalized,
            )
        )

    def _format_result(self, result: Dict[str, Any]) -> str:
        operation = result.get("operation")

        if operation == "none":
            return result.get("message") or "This request does not map to a database action."

        if operation == "read":
            rows = result.get("rows", [])
            if not rows:
                return "No matching records found."

            preview_size = min(20, len(rows))
            preview = rows[:preview_size]
            lines: List[str] = []

            for index, row in enumerate(preview, start=1):
                parts: List[str] = []
                for key, value in row.items():
                    if key == "__table":
                        continue
                    parts.append(f"{key.replace('_', ' ')}: {value}")

                table_name = row.get("__table")
                if table_name:
                    parts.append(f"table: {table_name}")

                line_text = ", ".join(parts) if parts else "no fields"
                lines.append(f"{index}. {line_text}")

            header = f"Found {len(rows)} record(s):"
            if len(rows) > preview_size:
                header = f"Found {len(rows)} records (showing first {preview_size}):"

            return header + "\n" + "\n".join(lines)

        if operation == "create":
            return (
                f"Created record in table '{result.get('table')}'. "
                f"Affected rows: {result.get('affected_rows', 0)}. "
                f"Last insert id: {result.get('last_insert_id')}."
            )

        if operation == "update":
            return (
                f"Updated table '{result.get('table')}'. "
                f"Affected rows: {result.get('affected_rows', 0)}."
            )

        if operation == "delete":
            return (
                f"Deleted from table '{result.get('table')}'. "
                f"Affected rows: {result.get('affected_rows', 0)}."
            )

        return "Operation completed."

    def answer_question(self, question: str) -> str:
        if self._is_greeting(question):
            return (
                f"Hello! I can perform CRUD operations on any table in '{self.mysql_database}'. "
                "Ask me to create, read, update, or delete data."
            )

        prompt = self._build_prompt(question)
        model_output = self.llm_client.complete(prompt)

        action = self._extract_json(model_output)
        if not action:
            raise ValueError(
                "The LLM response did not contain valid JSON action output. "
                "Enable debug logging and inspect raw model output."
            )

        validated_action = self._validate_action(action)
        result = self._execute_action(validated_action)

        if result.get("operation") == "none":
            fallback = self._fallback_read_search(question)
            if fallback:
                return self._format_result(fallback)

        if result.get("operation") == "read" and not result.get("rows"):
            fallback = self._fallback_read_search(question)
            if fallback:
                return self._format_result(fallback)

        return self._format_result(result)

    def show_available_data(self) -> str:
        lines: List[str] = [f"Database: {self.mysql_database}", "Tables and row counts:"]

        with self.connection.cursor(dictionary=True) as cursor:
            for table_name in self.schema["tables"].keys():
                cursor.execute(f"SELECT COUNT(*) AS total_rows FROM `{table_name}`")
                count = (cursor.fetchone() or {}).get("total_rows", 0)
                lines.append(f"- {table_name}: {count}")

        return "\n".join(lines)

    def list_tables(self) -> List[str]:
        return list(self.schema["tables"].keys())

    def get_table_data(self, table_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        table = str(table_name).strip()
        if not table:
            raise ValueError("table_name is required.")
        if not self._is_valid_identifier(table):
            raise ValueError(f"Invalid table name: {table}")
        if table not in self.schema["tables"]:
            raise ValueError(f"Table '{table}' does not exist in database '{self.mysql_database}'.")

        safe_limit = min(max(1, int(limit)), self.max_read_rows)
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(f"SELECT * FROM `{table}` LIMIT %s", (safe_limit,))
            return cursor.fetchall() or []

    def close(self) -> None:
        if getattr(self, "connection", None) and self.connection.is_connected():
            self.connection.close()
