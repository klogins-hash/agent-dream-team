"""Advanced tools for enhanced agent capabilities."""

from strands import tool
import json
from datetime import datetime


@tool
def web_search(query: str, num_results: int = 5) -> str:
    """Search the web for current information.
    
    Args:
        query: Search query
        num_results: Number of results to return (default: 5)
        
    Returns:
        Search results with titles and snippets
    """
    # TODO: Integrate with actual search API (DuckDuckGo, Brave, etc.)
    return f"""Web Search Results for: "{query}"

[Placeholder - Integrate with search API]

Suggested integrations:
- DuckDuckGo API (free, no key needed)
- Brave Search API
- SerpAPI
- Tavily AI Search

Example results would appear here with:
- Title
- URL
- Snippet
- Relevance score
"""


@tool
def read_file(filepath: str) -> str:
    """Read content from a file.
    
    Args:
        filepath: Path to the file to read
        
    Returns:
        File contents
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"File: {filepath}\n\n{content}"
    except FileNotFoundError:
        return f"Error: File not found: {filepath}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def write_file(filepath: str, content: str) -> str:
    """Write content to a file.
    
    Args:
        filepath: Path where to write the file
        content: Content to write
        
    Returns:
        Success message
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"✅ Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool
def list_files(directory: str = ".") -> str:
    """List files in a directory.
    
    Args:
        directory: Directory path (default: current directory)
        
    Returns:
        List of files and directories
    """
    import os
    try:
        items = os.listdir(directory)
        files = [f"📄 {item}" for item in items if os.path.isfile(os.path.join(directory, item))]
        dirs = [f"📁 {item}" for item in items if os.path.isdir(os.path.join(directory, item))]
        
        result = f"Contents of {directory}:\n\n"
        if dirs:
            result += "Directories:\n" + "\n".join(sorted(dirs)) + "\n\n"
        if files:
            result += "Files:\n" + "\n".join(sorted(files))
        
        return result
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@tool
def get_current_time() -> str:
    """Get the current date and time.
    
    Returns:
        Current date and time in readable format
    """
    now = datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"


@tool
def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression.
    
    Args:
        expression: Mathematical expression to evaluate
        
    Returns:
        Result of the calculation
    """
    try:
        # Safe evaluation - only allow math operations
        allowed_chars = set('0123456789+-*/().% ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters"
        
        result = eval(expression, {"__builtins__": {}}, {})
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"


@tool
def create_json(data: dict) -> str:
    """Format data as JSON.
    
    Args:
        data: Dictionary to convert to JSON
        
    Returns:
        Formatted JSON string
    """
    try:
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error creating JSON: {str(e)}"


@tool
def parse_json(json_string: str) -> str:
    """Parse a JSON string.
    
    Args:
        json_string: JSON string to parse
        
    Returns:
        Parsed data description
    """
    try:
        data = json.loads(json_string)
        return f"Parsed JSON:\n{json.dumps(data, indent=2)}"
    except Exception as e:
        return f"Error parsing JSON: {str(e)}"


@tool
def summarize_text(text: str, max_sentences: int = 3) -> str:
    """Create a brief summary of text.
    
    Args:
        text: Text to summarize
        max_sentences: Maximum sentences in summary
        
    Returns:
        Summary of the text
    """
    # Simple sentence-based summarization
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    if len(sentences) <= max_sentences:
        return text
    
    # Take first, middle, and last sentences for basic summary
    summary_sentences = []
    if max_sentences >= 1:
        summary_sentences.append(sentences[0])
    if max_sentences >= 2:
        summary_sentences.append(sentences[len(sentences)//2])
    if max_sentences >= 3:
        summary_sentences.append(sentences[-1])
    
    return '. '.join(summary_sentences) + '.'


@tool
def word_count(text: str) -> str:
    """Count words, characters, and sentences in text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Statistics about the text
    """
    words = len(text.split())
    chars = len(text)
    chars_no_spaces = len(text.replace(' ', ''))
    sentences = len([s for s in text.split('.') if s.strip()])
    
    return f"""Text Statistics:
- Words: {words}
- Characters (with spaces): {chars}
- Characters (no spaces): {chars_no_spaces}
- Sentences: {sentences}
- Average word length: {chars_no_spaces/words:.1f} characters
"""
