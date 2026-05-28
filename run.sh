#!/bin/bash
# استفاده از پورت تعیین شده توسط Render
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
