"""
Configuration system for OWL-MCP session-wide settings.

This module provides a configuration system that stores ontology metadata
and settings in a YAML file. The default location is ~/.owl-mcp/config.yaml.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger("owl-mcp.config")

# Default configuration directory
DEFAULT_CONFIG_DIR = Path.home() / ".owl-mcp"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"


class OntologyConfig(BaseModel):
    """Configuration for a single ontology."""

    path: str
    metadata_axioms: List[str] = Field(default_factory=list)
    readonly: bool = False
    description: Optional[str] = None
    preferred_serialization: Optional[str] = None
    annotation_property: Optional[str] = None

    def name(self) -> str:
        """Get the name of the ontology from its path."""
        return Path(self.path).stem


class OWLMCPConfig(BaseModel):
    """Main configuration model for OWL-MCP."""

    ontologies: Dict[str, OntologyConfig] = Field(default_factory=dict)
    default_serialization: str = "ofn"
    enable_auto_discovery: bool = True
    log_level: str = "INFO"
    
    # Additional session-wide settings
    editor_command: Optional[str] = None
    default_namespace: Optional[str] = None


class ConfigManager:
    """Manages OWL-MCP configuration."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file. 
                         If None, uses the default location.
        """
        self.config_path = config_path or DEFAULT_CONFIG_FILE
        self.config = self._load_config()

    def _load_config(self) -> OWLMCPConfig:
        """
        Load configuration from file or create default.
        
        Returns:
            OWLMCPConfig: The loaded or default configuration
        """
        if not self.config_path.exists():
            return self._create_default_config()
        
        try:
            with open(self.config_path, "r") as f:
                config_data = yaml.safe_load(f)
            
            if not config_data:
                return self._create_default_config()
                
            return OWLMCPConfig.model_validate(config_data)
        except (ValidationError, yaml.YAMLError) as e:
            logger.error(f"Error loading configuration from {self.config_path}: {e}")
            logger.info("Using default configuration instead")
            return self._create_default_config()
    
    def _create_default_config(self) -> OWLMCPConfig:
        """
        Create and save a default configuration.
        
        Returns:
            OWLMCPConfig: The default configuration
        """
        config = OWLMCPConfig()
        self.save_config(config)
        return config
    
    def save_config(self, config: Optional[OWLMCPConfig] = None) -> None:
        """
        Save the configuration to file.
        
        Args:
            config: The configuration to save. If None, saves the current config.
        """
        if config is not None:
            self.config = config
            
        # Ensure the config directory exists
        os.makedirs(self.config_path.parent, exist_ok=True)
        
        try:
            with open(self.config_path, "w") as f:
                yaml.dump(self.config.model_dump(), f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Error saving configuration to {self.config_path}: {e}")
    
    def add_ontology(self, 
                     name: str, 
                     path: str, 
                     metadata_axioms: Optional[List[str]] = None, 
                     readonly: bool = False,
                     description: Optional[str] = None,
                     preferred_serialization: Optional[str] = None,
                     annotation_property: Optional[str] = None) -> None:
        """
        Add or update an ontology configuration.
        
        Args:
            name: Name identifier for the ontology
            path: Absolute path to the ontology file
            metadata_axioms: List of metadata axioms as strings
            readonly: Whether the ontology is read-only
            description: Optional description of the ontology
            preferred_serialization: Optional preferred serialization format
            annotation_property: Optional annotation property IRI for labels
        """
        self.config.ontologies[name] = OntologyConfig(
            path=path,
            metadata_axioms=metadata_axioms or [],
            readonly=readonly,
            description=description,
            preferred_serialization=preferred_serialization,
            annotation_property=annotation_property
        )
        self.save_config()
    
    def remove_ontology(self, name: str) -> bool:
        """
        Remove an ontology from the configuration.
        
        Args:
            name: Name of the ontology to remove
            
        Returns:
            bool: True if the ontology was removed, False otherwise
        """
        if name in self.config.ontologies:
            del self.config.ontologies[name]
            self.save_config()
            return True
        return False
    
    def get_ontology(self, name: str) -> Optional[OntologyConfig]:
        """
        Get the configuration for a specific ontology.
        
        Args:
            name: Name of the ontology
            
        Returns:
            Optional[OntologyConfig]: The ontology configuration or None if not found
        """
        return self.config.ontologies.get(name)
    
    def get_ontology_by_path(self, path: str) -> Optional[OntologyConfig]:
        """
        Get the configuration for an ontology by its path.
        
        Args:
            path: Path to the ontology file
            
        Returns:
            Optional[OntologyConfig]: The ontology configuration or None if not found
        """
        path = str(Path(path).absolute())
        for ontology in self.config.ontologies.values():
            if str(Path(ontology.path).absolute()) == path:
                return ontology
        return None
    
    def list_ontologies(self) -> Dict[str, OntologyConfig]:
        """
        Get all configured ontologies.
        
        Returns:
            Dict[str, OntologyConfig]: Dictionary of ontology configurations
        """
        return self.config.ontologies


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: Optional[Path] = None) -> ConfigManager:
    """
    Get the global configuration manager instance.
    
    Args:
        config_path: Optional custom path to the configuration file
        
    Returns:
        ConfigManager: The configuration manager instance
    """
    global _config_manager
    if _config_manager is None or config_path is not None:
        _config_manager = ConfigManager(config_path)
    return _config_manager