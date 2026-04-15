# LLM Database Chatbot

This project connects a MySQL database to an NVIDIA LLM endpoint and answers database-related questions using data from `product_demo_db`.

## Setup

1. Install dependencies:

```powershell
python -m pip install -U pip
python -m pip install .
```

2. Set environment variables:

```powershell
set NVIDIA_API_KEY=your_nvidia_api_key
set NVIDIA_API_URL=https://api.nvidia.com/v1/engines/gpt-35-turbo/completions
set MYSQL_HOST=localhost
set MYSQL_PORT=3306
set MYSQL_USER=root
set MYSQL_PASSWORD=your_password
set MYSQL_DATABASE=product_demo_db
```

3. Run the chatbot:

```powershell
python main.py
```

## Usage

Ask any question about the database, for example:

- "List all products in the product table."
- "Show the top 5 product sales."
- "What categories exist in product_category?"

The chatbot will generate a SELECT query, execute it against MySQL, and return the query plus results.

## Supported tables

- `product_category`
- `product`
- `product_sales`
