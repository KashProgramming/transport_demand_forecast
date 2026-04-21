"""
Quick test script to verify Prophet model works without file handle issues
"""
import logging
import pandas as pd
import numpy as np
from models.prophet_model import ProphetForecaster

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('prophet').setLevel(logging.WARNING)
logging.getLogger('cmdstanpy').setLevel(logging.WARNING)

def test_prophet():
    """Test Prophet model with predict_in_sample"""
    print("Testing Prophet model...")
    
    # Create sample time series data
    dates = pd.date_range(start='2025-01-01', periods=100, freq='H')
    values = np.sin(np.arange(100) * 0.1) * 10 + 50 + np.random.randn(100) * 2
    train_data = pd.Series(values[:80], index=dates[:80])
    test_data = pd.Series(values[80:], index=dates[80:])
    
    # Initialize and fit model
    print("Initializing Prophet...")
    model = ProphetForecaster()
    
    print("Fitting model...")
    model.fit(train_data)
    
    print("Making predictions with predict_in_sample (this tests the refit loop)...")
    predictions = model.predict_in_sample(test_data)
    
    print(f"✓ Successfully generated {len(predictions)} predictions")
    print(f"  Predictions shape: {predictions.shape}")
    print(f"  Sample predictions: {predictions[:5]}")
    
    # Test regular predict
    print("\nTesting regular predict...")
    future_predictions = model.predict(steps=10)
    print(f"✓ Successfully generated {len(future_predictions)} future predictions")
    
    print("\n✅ All tests passed! Prophet model is working correctly.")
    return True

if __name__ == "__main__":
    try:
        test_prophet()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
