"""
Client for direct forecasting using Chronos model integration.
"""
import logging
import pandas as pd
import numpy as np
import torch
import os
from typing import Dict, List, Union, Optional, Any
from chronos import BaseChronosPipeline

# Configure logging
logger = logging.getLogger(__name__)

class IntegratedForecastClient:
    """Client for direct forecasting using integrated Chronos model."""
    
    def __init__(self, model_name: str = "amazon/chronos-bolt-base", device_map: str = "cpu"):
        """
        Initialize the integrated forecast client.
        
        Args:
            model_name (str): Name of the Chronos model to use
            device_map (str): Device mapping for the model (cpu/cuda)
        """
        self.model_name = model_name
        self.device_map = device_map
        self.pipeline = None
        
        # Store last forecast result
        self.last_forecast = None
        
        # Initialize the model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Chronos model pipeline."""
        try:
            hf_token = os.getenv("HF_TOKEN")
            if not hf_token:
                logger.warning("HF_TOKEN not found in environment variables. Model loading may fail for gated models.")
            
            logger.info(f"Loading Chronos model: {self.model_name}")
            self.pipeline = BaseChronosPipeline.from_pretrained(
                self.model_name,
                device_map=self.device_map,
                torch_dtype=torch.bfloat16,
                use_auth_token=hf_token
            )
            logger.info("Chronos model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Chronos model: {str(e)}")
            raise RuntimeError(f"Failed to initialize Chronos model: {str(e)}")
    
    @staticmethod
    def infer_date_format(date_str):
        """
        Infer the date format from a string representation.
        
        Args:
            date_str (str): String representation of a date
            
        Returns:
            str: Inferred date format
        """
        formats = [
            '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y',
            '%Y%m%d', '%d%m%Y', '%m%d%Y',
            '%Y-%m-%d %H:%M:%S', '%d-%m-%Y %H:%M:%S', '%m-%d-%Y %H:%M:%S'
        ]
        
        for fmt in formats:
            try:
                pd.to_datetime(date_str, format=fmt)
                return fmt
            except (ValueError, TypeError):
                continue
        
        return None  # Default to None if no format matches
    
    def forecast(
        self, 
        data: pd.DataFrame, 
        target_column: str, 
        date_column: str = None,
        prediction_length: int = 30,
        return_extended_df: bool = True
    ) -> Union[pd.DataFrame, Dict]:
        """
        Generate forecasts for time series data using the integrated Chronos model.
        
        Args:
            data (pd.DataFrame): DataFrame containing the time series data
            target_column (str): Name of the column to forecast
            date_column (str, optional): Name of the date/time column. If None, first column is used.
            prediction_length (int, optional): Number of periods to forecast
            return_extended_df (bool, optional): If True, returns extended DataFrame; otherwise returns forecast dict
            
        Returns:
            Union[pd.DataFrame, Dict]: Extended DataFrame with forecasts or forecast results dictionary
        """
        try:
            # Validate inputs
            if target_column not in data.columns:
                raise ValueError(f"Target column '{target_column}' not found in DataFrame")
            
            if prediction_length <= 0:
                raise ValueError("prediction_length must be greater than 0")
            
            # Use first column as date column if not specified
            if date_column is None:
                date_column = data.columns[0]
                logger.info(f"Using {date_column} as date column")
            
            # Create a copy to avoid modifying the original
            current_df = data.copy()
            
            # Prepare the context tensor for Chronos
            try:
                context_values = current_df[target_column].dropna().values
                if len(context_values) == 0:
                    raise ValueError(f"No valid values found in target column '{target_column}'")
                
                context = torch.tensor(context_values, dtype=torch.float32)
                logger.info(f"Prepared context tensor with {len(context_values)} values")
                
            except Exception as e:
                raise ValueError(f"Error preparing context data: {str(e)}")
            
            # Generate forecast using Chronos
            logger.info(f"Generating forecast with prediction_length={prediction_length}")
            forecast_tensor = self.pipeline.predict(
                context=context, 
                prediction_length=prediction_length
            )
            
            # Extract quantiles for confidence intervals
            quantiles = [0.1, 0.9]
            quantile_indices = [int(q * forecast_tensor.shape[1]) for q in quantiles]
            lower_quantile = forecast_tensor[0, quantile_indices[0], :].cpu().numpy()
            upper_quantile = forecast_tensor[0, quantile_indices[1], :].cpu().numpy()
            
            # Get median forecast
            median_quantile_index = forecast_tensor.shape[1] // 2
            median_forecast = forecast_tensor[0, median_quantile_index, :].cpu().numpy()
            
            # Create forecast result dictionary
            actual_data = context_values.tolist()
            forecast_horizon = list(range(len(actual_data), len(actual_data) + len(median_forecast)))
            
            self.last_forecast = {
                "actual": actual_data,
                "forecast": median_forecast.tolist(),
                "horizon": forecast_horizon,
                "lower_quantile": lower_quantile.tolist(),
                "upper_quantile": upper_quantile.tolist()
            }
            
            logger.info("Forecast generated successfully")
            
            # If only forecast data is requested, return it
            if not return_extended_df:
                return self.last_forecast
            
            # Process to extend the dataframe with forecast values
            extended_values = self.last_forecast['actual'] + self.last_forecast['forecast']
            lower_quantile_extended = [None for _ in range(len(self.last_forecast['actual']))] + self.last_forecast['lower_quantile']
            upper_quantile_extended = [None for _ in range(len(self.last_forecast['actual']))] + self.last_forecast['upper_quantile']
            future_assigned = [False] * len(self.last_forecast['actual']) + [True] * len(self.last_forecast['forecast'])
            
            # Ensure date column is datetime
            current_df[date_column] = pd.to_datetime(current_df[date_column], format='mixed', utc=True)
            
            # Infer frequency from dates
            dates = current_df[date_column]
            freq = pd.infer_freq(dates)
            if freq is None:
                # Try to infer a reasonable frequency if pandas can't
                if len(dates) >= 2:
                    # Calculate average time difference
                    avg_diff = (dates.iloc[-1] - dates.iloc[0]) / (len(dates) - 1)
                    if avg_diff.days >= 28 and avg_diff.days <= 31:
                        freq = 'M'  # Monthly
                    elif avg_diff.days >= 7 and avg_diff.days <= 7.5:
                        freq = 'W'  # Weekly
                    elif avg_diff.days >= 0.9 and avg_diff.days <= 1.1:
                        freq = 'D'  # Daily
                    else:
                        freq = 'D'  # Default to daily
                else:
                    freq = 'D'  # Default if can't infer
            
            # Generate future dates
            future_dates = pd.date_range(start=dates.iloc[-1], periods=prediction_length + 1, freq=freq)[1:]
            
            # Extend the DataFrame with future dates
            extended_df = pd.concat([
                current_df, 
                pd.DataFrame({date_column: future_dates})
            ]).reset_index(drop=True)
            
            # Add the forecast values and metrics
            extended_df[target_column] = pd.Series(extended_values[:len(extended_df)])
            extended_df['future_assigned'] = pd.Series(future_assigned[:len(extended_df)])
            extended_df['lower_quantile'] = pd.Series(lower_quantile_extended[:len(extended_df)])
            extended_df['upper_quantile'] = pd.Series(upper_quantile_extended[:len(extended_df)])
            
            logger.info(f"Extended DataFrame created with {len(future_dates)} forecast periods")
            
            # Return the extended DataFrame
            return extended_df
            
        except Exception as e:
            logger.error(f"Error generating forecast: {str(e)}")
            return {"error": f"Error generating forecast: {str(e)}"}

# Backward compatibility: Create aliases for existing classes
ForecastClient = IntegratedForecastClient

# Standalone function for direct registration with function registry
def generate_forecast(
    data: pd.DataFrame, 
    target_column: str, 
    date_column: str = None,
    prediction_length: int = 30,
) -> pd.DataFrame:
    """
    Generate time series forecasts and extend the dataframe with predicted values.
    
    Args:
        data (pd.DataFrame): DataFrame containing the time series data
        target_column (str): Name of the column to forecast
        date_column (str, optional): Name of the date/time column. If None, first column is used.
        prediction_length (int, optional): Number of periods to forecast
        
    Returns:
        pd.DataFrame: Extended DataFrame with forecast values and confidence intervals
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Create an integrated client instance
        client = IntegratedForecastClient()
        
        # Execute forecast
        result = client.forecast(
            data=data,
            target_column=target_column,
            date_column=date_column,
            prediction_length=prediction_length
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in generate_forecast function: {str(e)}")
        return {"error": f"Error generating forecast: {str(e)}"}