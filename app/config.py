import os

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

# Analysis settings
TOP_20_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "SHIBUSDT", "DOTUSDT",
    "LINKUSDT", "TRXUSDT", "MATICUSDT", "LTCUSDT", "NEARUSDT",
    "UNIUSDT", "BCHUSDT", "ARBUSDT", "APTUSDT", "OPUSDT"
]

TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1d", "1w", "1M"]

# Similarity
SIMILARITY_THRESHOLD = 0.92

# Candles
PATTERN_START_INDEX = 6   # candle 7
PATTERN_END_INDEX = 9     # candle 9 inclusive in human terms, Python slice end is exclusive
METRIC_CANDLE_INDEX = 5   # candle 6
MIN_CANDLES_REQUIRED = 10 # need at least 10 candles to have candle 6 + 7..9

# Search
MAX_MATCHES = 5
SCAN_LIMIT = 200
