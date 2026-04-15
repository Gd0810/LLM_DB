# LLM Database Chatbot

This project connects a MySQL database to an NVIDIA LLM endpoint and answers database-related questions using data from `product_demo_db`.

## Setup

1. Install dependencies:

```powershell
python -m pip install -U pip
python -m pip install .
```

2. Create a `.env` file in the project root with the variables below, or set them in your shell:

```powershell
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_API_KEY=your_nvidia_api_key
NVIDIA_MODEL=openai/gpt-oss-120b
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=product_demo_db
```

You can also keep using the old NVIDIA API URL format by setting `NVIDIA_API_URL` instead of `NVIDIA_BASE_URL`.

If you prefer, install from `requirements.txt` instead of the package:

```powershell
python -m pip install -r requirements.txt
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
