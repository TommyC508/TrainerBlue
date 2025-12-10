"""Configuration management."""
import os
from pathlib import Path
from typing import Any, Dict
import yaml
from dotenv import load_dotenv


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        return {}
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    return config or {}


def load_env():
    """Load environment variables from .env file."""
    load_dotenv()


def get_env(key: str, default: Any = None) -> Any:
    """
    Get environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        Environment variable value or default
    """
    return os.getenv(key, default)
