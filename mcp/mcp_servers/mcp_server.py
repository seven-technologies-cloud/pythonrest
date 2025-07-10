from mcp.server.fastmcp import FastMCP
import logging
import requests
import json
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file using direct path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
env_path = os.path.join(parent_dir, ".env")
logger.info(f"Loading .env file from: {env_path}")
load_dotenv(dotenv_path=env_path)

# PostgreSQL connection string
DB_STRING = os.getenv("DB_STRING")
API_KEY = os.getenv("API_KEY")
if not DB_STRING:
    logger.error("DB_STRING environment variable not found. Check your .env file.")
else:
    logger.info("DB_STRING environment variable loaded successfully.")

# Create the FastMCP instance
mcp = FastMCP("MeuServidorMCP")

@mcp.tool()
def hello_world():
    return "Hello from FastMCP!"

@mcp.tool()
def get_database_tables_tool(user_query: str = ""):
    """
    Gets information from the database based on the user's query.    
    Args:
        user_query (str): The user's query to determine what information to return    
    Returns:
        Information from the database formatted according to the user's query.
    """
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Connect to the database
        conn = psycopg2.connect(DB_STRING)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        
        if not tables:
            return {"message": "No tables found in the database", "available_tables": []}
        
        table_names = [table['table_name'] for table in tables]
        
        # If no user query is provided, return all table names
        if not user_query:
            cur.close()
            conn.close()
            return {"available_tables": table_names}
        
        # Use LLM to analyze the user's query and determine the required information
        query_analysis = _analyze_query_with_llm(user_query, table_names)
        
        # If the LLM analysis suggests only returning table names
        if query_analysis.get("return_only_names", False):
            cur.close()
            conn.close()
            return {"available_tables": table_names}
        
        # If the query asks for more details, fetch the full information
        db_info = _get_full_database_info(cur, conn, tables)
        
        # Use LLM to format the response based on the user's query
        formatted_response = _format_response_with_llm(user_query, db_info)
        
        cur.close()
        conn.close()
        
        return formatted_response
        
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return {"error": str(e)}


def _get_full_database_info(cur, conn, tables):
    """
    Gets full information about all tables in the database.
    
    Args:
        cur: Database cursor
        conn: Database connection
        tables: List of tables
        
    Returns:
        Dictionary containing information about all tables
    """
    result = {
        "available_tables": [table['table_name'] for table in tables],
        "table_details": {}
    }
    
    for table in tables:
        table_name = table['table_name']
        try:
            # Get column information
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            columns = cur.fetchall()
            
            # Get sample data (up to 2000 rows)
            cur.execute(f'SELECT * FROM "{table_name}" LIMIT 2000')
            sample_data = cur.fetchall()
            
            result["table_details"][table_name] = {
                'columns': columns,
                'sample_data': sample_data
            }
        except Exception as table_error:
            logger.error(f"Error processing table {table_name}: {str(table_error)}")
            result["table_details"][table_name] = {
                'error': str(table_error),
                'columns': [],
                'sample_data': []
            }
            # Rollback the transaction for this table
            conn.rollback()
    
    return result

def _analyze_query_with_llm(user_query: str, table_names: list) -> dict:
    """
    Uses LLM to analyze the user's query and determine what information to return.
    
    Args:
        user_query (str): The user's query
        table_names (list): List of available table names
        
    Returns:
        dict: Analysis of the query with recommendations
    """
    if not user_query:
        return {"return_only_names": False}
        
    try:
        # Use the Gemini API to analyze the query
        prompt = f"""
        Analyze the following user query about a database and determine what information to return.
        
        Available tables: {', '.join(table_names)}
        
        User query: {user_query}
        
        Determine:
        1. Should we return only table names? (true/false)
        2. Are there specific tables mentioned in the query? (list them)
        3. Are there specific columns mentioned in the query? (list them)
        4. What level of detail is requested? (minimal/moderate/detailed)
        
        Return a JSON object with these keys:
        {{
            "return_only_names": true/false,
            "specific_tables": ["table1", "table2"],
            "specific_columns": ["column1", "column2"],
            "detail_level": "minimal/moderate/detailed"
        }}
        
        If no specific tables or columns are mentioned, use empty lists.
        """
        
        response = requests.post(
            "http://localhost:8000/generate",
            json={"prompt": prompt, "api_key": API_KEY},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        result_text = data["response"].strip()
        
        # Extract JSON from the response
        try:
            # Find JSON in the response
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = result_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                logger.error(f"Could not find JSON in LLM response: {result_text}")
                return {"return_only_names": False}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from LLM response: {str(e)}")
            return {"return_only_names": False}
            
    except Exception as e:
        logger.error(f"Error analyzing query with LLM: {str(e)}")
        # Default to returning full details if there's an error
        return {"return_only_names": False}

def _format_response_with_llm(user_query: str, db_info: dict) -> dict:
    """
    Uses LLM to format the database information based on the user's query.
    
    Args:
        user_query (str): The user's query
        db_info (dict): Full database information
        
    Returns:
        dict: Formatted response based on the user's query
    """
    try:
        # Convert db_info to a string representation for the prompt
        db_info_str = json.dumps(db_info)
        
        # Use the Gemini API to format the response
        prompt = f"""
        Format the following database information based on the user's query.
        
        User query: {user_query}
        
        Database information: {db_info_str}
        
        Return a JSON object with the following structure:
        {{
            "response_type": "table_names/table_details/column_info/sample_data/custom",
            "formatted_data": {{
                // Formatted data based on the user's query
            }}
        }}
        
        The formatted_data should contain only the information relevant to the user's query.
        If the user is asking for table names, include only the table names.
        If the user is asking for specific columns, include only those columns.
        If the user is asking for sample data, include only the relevant sample data.
        """
        
        response = requests.post(
            "http://localhost:8000/generate",
            json={"prompt": prompt, "api_key": API_KEY},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        result_text = data["response"].strip()
        
        # Extract JSON from the response
        try:
            # Find JSON in the response
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = result_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                logger.error(f"Could not find JSON in LLM response: {result_text}")
                return db_info
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from LLM response: {str(e)}")
            return db_info
            
    except Exception as e:
        logger.error(f"Error formatting response with LLM: {str(e)}")
        # Default to returning the full database info if there's an error
        return db_info

if __name__ == "__main__":
    try:
        logger.info("Starting MCP server...")
        logger.info(f"Using PostgreSQL database")
        mcp.run()
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
