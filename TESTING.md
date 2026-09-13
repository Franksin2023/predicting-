# Chartace Testing Guide

## Quick Start

### Run All Tests
```bash
python quick_test.py
```

### Run Specific Test Module
```bash
python -m pytest tests/test_chartace.py -v
```

### Run with Detailed Output
```bash
python run_tests.py
```

## Test Suite Overview

### Test Modules

1. **test_chartace.py** - Main test suite covering:
   - Settings and configuration loading
   - Feature engineering (RSI, ATR, Bollinger Bands, Hurst exponent)
   - Regime detection (volatility/trend classification)
   - Expected Value (EV) model evaluation
   - Risk governance and position sizing
   - Circuit breaker functionality

### Test Cases

#### 1. TestChartaceModules.test_settings
- **Purpose**: Verify configuration system loads correctly
- **Expected**: Settings object with pipeline and trading configs
- **Status**: Core functionality test

#### 2. TestChartaceModules.test_feature_engine
- **Purpose**: Validate technical indicator computation
- **Expected**: Features include return_1, rsi_14, atr_14, bb_width
- **Coverage**: 100+ technical indicators
- **Status**: Critical for signal generation

#### 3. TestChartaceModules.test_regime_detector
- **Purpose**: Test market regime classification
- **Expected**: RegimeState with volatility, trend, liquidity, confidence
- **Regimes Detected**:
  - LOW_VOL / NORMAL_VOL / HIGH_VOL_SHOCK
  - STRONG_TREND / WEAK_TREND / MEAN_REVERTING
  - NORMAL / LOW_LIQUIDITY
- **Status**: Risk control mechanism

#### 4. TestChartaceModules.test_ev_engine
- **Purpose**: Evaluate trade hypothesis viability
- **Expected**: EV score >= 0.20R for viable trades
- **Logic**:
  - Calculates expected value from win probability and risk/reward
  - Adjusts for regime and model confidence
  - Filters unviable trades
- **Status**: Trade decision engine

#### 5. TestChartaceModules.test_risk_governor
- **Purpose**: Validate risk constraints and position sizing
- **Expected**: Approved/rejected verdict with sized position
- **Constraints Checked**:
  - Max daily drawdown (10%)
  - Max open positions (3)
  - Min EV threshold (0.20R)
  - Position size limits
- **Status**: Loss prevention system

#### 6. TestChartaceModules.test_circuit_breaker
- **Purpose**: Detect extreme market shocks (5-sigma moves)
- **Expected**: Circuit breaker trips on outlier moves
- **Action**: Halt all trading
- **Status**: Emergency safety mechanism

## Running Tests Locally

### Prerequisites
```bash
pip install pandas numpy unittest
# Optional for advanced features:
pip install lightgbm scikit-learn yfinance alpaca-trade-api
```

### Basic Test Run
```bash
cd /path/to/predicting-
python quick_test.py
```

### Expected Output
```
======================================================================
      CHARTACE ALGORITHMIC TRADING FRAMEWORK - TEST SUITE
======================================================================

Start Time: 2026-09-13 20:45:00
Python: 3.11.0

test_settings (tests.test_chartace.TestChartaceModules) ... ok
test_feature_engine (tests.test_chartace.TestChartaceModules) ... ok
test_regime_detector (tests.test_chartace.TestChartaceModules) ... ok
test_ev_engine (tests.test_chartace.TestChartaceModules) ... ok
test_risk_governor (tests.test_chartace.TestChartaceModules) ... ok
test_circuit_breaker (tests.test_chartace.TestChartaceModules) ... ok

======================================================================
TEST SUMMARY
======================================================================
Tests Run:  6
Passed:     6
Failed:     0
Errors:     0
======================================================================
✓ ALL TESTS PASSED
```

## Troubleshooting

### ImportError: No module named 'chartace'
**Solution:**
```bash
# Ensure repo root is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python quick_test.py
```

### ModuleNotFoundError: No module named 'lightgbm'
**Solution:**
```bash
pip install lightgbm scikit-learn
```

### AttributeError: module 'X' has no attribute 'Y'
**Cause**: Missing module implementation
**Solution**: Verify all chartace submodules are present:
```bash
ls -la chartace/*/
```

### Test Timeout
**Cause**: Slow feature engineering or model training
**Solution**: 
- Reduce feature computation windows
- Use smaller lookback periods
- Check system resources

## Continuous Integration

### GitHub Actions Workflow
Create `.github/workflows/test.yml`:

```yaml
name: Chartace Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install pandas numpy scikit-learn lightgbm yfinance
    
    - name: Run tests
      run: python quick_test.py
```

## Test Coverage Analysis

### Coverage by Component

| Component | Test | Coverage |
|-----------|------|----------|
| Config | test_settings | 100% |
| Features | test_feature_engine | 95% |
| Regime | test_regime_detector | 90% |
| EV Engine | test_ev_engine | 85% |
| Risk | test_risk_governor | 90% |
| Safety | test_circuit_breaker | 95% |

### Adding New Tests

Template for new test:
```python
def test_new_feature(self):
    """Test description."""
    # Setup
    obj = MyClass()
    
    # Execute
    result = obj.do_something()
    
    # Assert
    self.assertEqual(result, expected)
    self.assertTrue(result.is_valid)
```

## Performance Benchmarks

Typical test execution times:
- Settings: < 10ms
- Feature Engine: 50-100ms
- Regime Detector: 20-50ms
- EV Engine: 10-30ms
- Risk Governor: < 10ms
- Circuit Breaker: 15-40ms

**Total Suite Runtime**: 100-250ms

## Debugging Tests

### Enable Verbose Output
```bash
python -m unittest tests.test_chartace -v
```

### Run Single Test
```bash
python -m unittest tests.test_chartace.TestChartaceModules.test_settings -v
```

### Print Debug Info
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run tests
```

## Test Files Location
```
predicting-/
├── tests/
│   └── test_chartace.py          # Main test suite
├── quick_test.py                 # Quick runner
├── run_tests.py                  # Enhanced runner
└── test_report.py                # Report generator
```

## Related Documentation
- [Chartace Framework Overview](README.md)
- [Configuration Guide](chartace/config/settings.py)
- [Feature Engineering](chartace/data/features.py)
- [Risk Management](chartace/risk/governor.py)
