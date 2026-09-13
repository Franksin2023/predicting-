# Chartace Application Startup Guide

## Quick Start

### Option 1: Run Python Startup (Recommended)
```bash
python startup.py
```

### Option 2: Run Shell Startup
```bash
bash startup.sh
```

### Option 3: Run with Alpaca Trading
```bash
export ALPACA_API_KEY="your_alpaca_api_key"
export ALPACA_SECRET_KEY="your_alpaca_secret_key"
python startup.py
```

---

## What Happens on Startup

### 1. **Dependency Check** ✓
- Verifies Python 3.7+ is installed
- Checks required packages (pandas, numpy)
- Lists optional packages (yfinance, alpaca, lightgbm)

### 2. **Module Verification** ✓
- Loads all Chartace modules
- Checks configuration system
- Validates orchestrator initialization

### 3. **Component Initialization** ✓
- Initializes trading clients (Alpaca if credentials provided)
- Sets up portfolio synchronization
- Configures execution bridge
- Activates circuit breaker
- Initializes audit logger

### 4. **Model Loading** ✓
- Attempts to load 3 pre-trained models:
  - `trend` model
  - `mean_reversion` model
  - `volatility` model
- Falls back to defaults if models not found

### 5. **Status Report** ✓
- Displays application configuration
- Shows active trading mode (paper/simulation)
- Lists configured symbols
- Shows risk parameters

### 6. **Event Logging** ✓
- Logs startup event to `logs/audit_trail.jsonl`
- Records system ready status

---

## Expected Output

```
================================================================================
                 CHARTACE FRAMEWORK - STARTUP CHECK
================================================================================

[1] Python Version: 3.11.0 (main, Oct  3 2023, 00:00:00)
    ✓ OK

[2] Checking Dependencies...
    ✓ pandas           - Data manipulation
    ✓ numpy            - Numerical computing

[3] Optional Dependencies...
    ✓ yfinance         - Market data (yFinance)
    ⚠ alpaca           - Market data (Alpaca) (optional)

[4] Checking Chartace Modules...
    ✓ Config module
    ✓ Data/Features module
    ✓ Regime Detection module
    ✓ EV Engine module
    ✓ Risk Governor module
    ✓ Circuit Breaker module
    ✓ Execution Bridge module
    ✓ Portfolio Sync module
    ✓ Audit Logger module
    ✓ Orchestrator module

[5] Checking Configuration...
    ✓ App Name: Chartace
    ✓ Log Level: INFO
    ✓ Risk Limits: 10.0% daily drawdown

================================================================================
✓ ALL STARTUP CHECKS PASSED
================================================================================

[6] Initializing Chartace Framework...
    ✓ Portfolio sync initialized
    ✓ Execution bridge initialized
    ✓ Trailing manager initialized
    ✓ Circuit breaker initialized
    ✓ Audit logger initialized
    ✓ Orchestrator initialized

================================================================================
[STARTUP] ChartAce 2.0 initialized successfully
================================================================================

[7] Application Status
    App Name: Chartace
    Mode: Simulation
    Max Drawdown: 10.0%
    Max Positions: 3
    Min EV: 0.2R
    Circuit Breaker: 5.0-sigma threshold

================================================================================
✓ CHARTACE FRAMEWORK READY
================================================================================

Next Steps:
  1. Configure API keys: export ALPACA_API_KEY=... && export ALPACA_SECRET_KEY=...
  2. Check audit logs: tail -f logs/audit_trail.jsonl
```

---

## Configuration Before Running

### Set Trading Credentials (Optional)
```bash
export ALPACA_API_KEY="PK1234567890ABCDEF"
export ALPACA_SECRET_KEY="your_secret_key_here"
```

### Create Model Files (Optional)
Place pre-trained models in `models/` directory:
```
models/
├── trend_model.pkl
├── mean_reversion_model.pkl
└── volatility_model.pkl
```

### Adjust Settings (Optional)
Edit `chartace/config/settings.py`

---

## Directory Structure After Startup

```
predicting-/
├── logs/
│   └── audit_trail.jsonl         # All trading events logged here
├── models/
│   ├── trend_model.pkl           # Optional pre-trained models
│   ├── mean_reversion_model.pkl
│   └── volatility_model.pkl
├── data/
│   └── features/                 # Cached feature data
├── startup.py                    # Application startup
├── startup.sh                    # Shell startup script
└── chartace/
    └── ... (framework files)
```

---

## Troubleshooting

### Error: "No module named 'pandas'"
```bash
pip install pandas numpy
python startup.py
```

### Error: "ImportError: cannot import name 'RiskGovernor'"
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python startup.py
```

### Error: "FileNotFoundError: logs directory"
```bash
mkdir -p logs models data
python startup.py
```

### Alpaca connection fails
- Verify API credentials: `echo $ALPACA_API_KEY`
- Check credentials are valid in Alpaca dashboard
- Remove credentials to run in simulation mode
- Check network connectivity

---

## Running Different Modes

### Simulation Mode (No Real Trading)
```bash
python startup.py
```

### Paper Trading (Alpaca Paper Account)
```bash
export ALPACA_API_KEY="your_key"
export ALPACA_SECRET_KEY="your_secret"
python startup.py
```

---

## Monitoring After Startup

### View Audit Log
```bash
tail -f logs/audit_trail.jsonl
```

### Parse Audit Log
```python
import json
with open('logs/audit_trail.jsonl') as f:
    for line in f:
        event = json.loads(line)
        print(f"{event['timestamp']}: {event['event_type']}")
```

### Check Status
```bash
ls -lah logs/
ls -lah models/
python -c "from chartace.config.settings import Settings; print(Settings())"
```

---

## Next Steps

1. Run startup: `python startup.py`
2. Verify all checks pass
3. Configure Alpaca credentials (optional)
4. Review `logs/audit_trail.jsonl`
5. Check `TEST_AND_RUN_SUMMARY.md` for next steps

---

**Status: ✅ READY TO RUN**
