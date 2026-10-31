# -*- coding: utf-8 -*-
"""
scripts/_init_paths.py
content_data 및 프로젝트 루트 경로를 sys.path에 자동 등록하는 헬퍼 모듈.
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DATA_DIR = os.path.join(REPO_ROOT, "content_data")

if CONTENT_DATA_DIR not in sys.path:
    sys.path.insert(0, CONTENT_DATA_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
