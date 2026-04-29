"""
Model Manager for saving and loading trained models
"""
import os
import pickle
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import pandas as pd

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages model persistence and loading"""
    
    def __init__(self, models_dir: str = "saved_models"):
        """
        Initialize Model Manager
        
        Args:
            models_dir: Directory to store saved models
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.metadata_file = self.models_dir / "metadata.json"
        
    def _generate_config_hash(self, config: Dict[str, Any]) -> str:
        """
        Generate hash from configuration to identify unique model sets
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Hash string
        """
        # Sort keys for consistent hashing
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()[:12]
    
    def _get_model_path(self, model_name: str, config_hash: str) -> Path:
        """Get path for a specific model"""
        return self.models_dir / f"{model_name}_{config_hash}.pkl"
    
    def _get_prophet_model_path(self, config_hash: str) -> Path:
        """Get path for Prophet model (uses JSON serialization)"""
        return self.models_dir / f"prophet_{config_hash}.json"
    
    def save_metadata(self, config: Dict[str, Any], config_hash: str):
        """
        Save metadata about the current model configuration
        
        Args:
            config: Configuration dictionary
            config_hash: Hash of the configuration
        """
        metadata = {
            'config_hash': config_hash,
            'config': config,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved metadata with hash: {config_hash}")
    
    def load_metadata(self) -> Optional[Dict[str, Any]]:
        """Load metadata if it exists"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return None
    
    def models_exist(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if models exist for the given configuration
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Tuple of (exists, config_hash)
        """
        config_hash = self._generate_config_hash(config)
        
        # Check if all model files exist
        model_names = ['arima', 'sarima', 'xgboost']
        all_exist = all(
            self._get_model_path(name, config_hash).exists() 
            for name in model_names
        )
        
        # Also check Prophet model
        prophet_exists = self._get_prophet_model_path(config_hash).exists()
        
        return (all_exist and prophet_exists, config_hash)
    
    def save_models(self, models: Dict[str, Any], config: Dict[str, Any]) -> str:
        """
        Save all trained models
        
        Args:
            models: Dictionary of trained models
            config: Configuration used for training
            
        Returns:
            Configuration hash
        """
        config_hash = self._generate_config_hash(config)
        
        logger.info(f"Saving models with config hash: {config_hash}")
        
        # Save ARIMA, SARIMA, XGBoost with pickle
        for model_name in ['ARIMA', 'SARIMA', 'XGBoost']:
            if model_name in models:
                model_path = self._get_model_path(model_name.lower(), config_hash)
                try:
                    with open(model_path, 'wb') as f:
                        pickle.dump(models[model_name], f)
                    logger.info(f"Saved {model_name} model to {model_path}")
                except Exception as e:
                    logger.error(f"Failed to save {model_name}: {e}")
        
        # Save Prophet model using its serialization
        if 'Prophet' in models:
            prophet_path = self._get_prophet_model_path(config_hash)
            try:
                # Prophet models can be serialized to JSON
                with open(prophet_path, 'w') as f:
                    from prophet.serialize import model_to_json
                    json.dump(model_to_json(models['Prophet'].model), f)
                logger.info(f"Saved Prophet model to {prophet_path}")
            except Exception as e:
                logger.error(f"Failed to save Prophet: {e}")
        
        # Save metadata
        self.save_metadata(config, config_hash)
        
        return config_hash
    
    def load_models(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Load models for the given configuration
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dictionary of loaded models or None if not found
        """
        exists, config_hash = self.models_exist(config)
        
        if not exists:
            logger.info("No saved models found for this configuration")
            return None
        
        logger.info(f"Loading models with config hash: {config_hash}")
        
        models = {}
        
        # Load ARIMA, SARIMA, XGBoost
        for model_name in ['ARIMA', 'SARIMA', 'XGBoost']:
            model_path = self._get_model_path(model_name.lower(), config_hash)
            try:
                with open(model_path, 'rb') as f:
                    models[model_name] = pickle.load(f)
                logger.info(f"Loaded {model_name} model from {model_path}")
            except Exception as e:
                logger.error(f"Failed to load {model_name}: {e}")
                return None
        
        # Load Prophet model
        prophet_path = self._get_prophet_model_path(config_hash)
        try:
            with open(prophet_path, 'r') as f:
                from prophet.serialize import model_from_json
                from models.prophet_model import ProphetForecaster
                
                prophet_forecaster = ProphetForecaster()
                prophet_forecaster.model = model_from_json(json.load(f))
                prophet_forecaster.fitted = True
                models['Prophet'] = prophet_forecaster
            logger.info(f"Loaded Prophet model from {prophet_path}")
        except Exception as e:
            logger.error(f"Failed to load Prophet: {e}")
            return None
        
        logger.info("All models loaded successfully")
        return models
    
    def clear_old_models(self, keep_latest: int = 3):
        """
        Clear old model files, keeping only the latest N configurations
        
        Args:
            keep_latest: Number of latest model sets to keep
        """
        # Get all model files with timestamps
        model_files = list(self.models_dir.glob("*.pkl")) + list(self.models_dir.glob("*.json"))
        
        if len(model_files) <= keep_latest * 4:  # 4 files per config (3 pkl + 1 json)
            return
        
        # Sort by modification time
        model_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Keep latest files
        files_to_keep = set(model_files[:keep_latest * 4])
        
        # Delete old files
        for file in model_files:
            if file not in files_to_keep and file.name != "metadata.json":
                try:
                    file.unlink()
                    logger.info(f"Deleted old model file: {file}")
                except Exception as e:
                    logger.error(f"Failed to delete {file}: {e}")
    
    def get_config_from_params(self, data_file: str, sample_size: Optional[int], 
                               train_split: float = 0.8, 
                               use_sample_in_hash: bool = True) -> Dict[str, Any]:
        """
        Create configuration dictionary from parameters
        
        Args:
            data_file: Path to data file
            sample_size: Sample size (None for full data)
            train_split: Train/test split ratio
            use_sample_in_hash: Whether to include sample_size in hash (False allows reusing models across different sample sizes)
            
        Returns:
            Configuration dictionary
        """
        config = {
            'data_file': data_file,
            'train_split': train_split,
            'version': '1.0'  # Increment this to force retraining
        }
        
        # Only include sample_size in hash if explicitly requested
        # This allows training on large dataset and inferring on smaller ones
        if use_sample_in_hash:
            config['sample_size'] = sample_size
            
        return config
