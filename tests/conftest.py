#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : conftest.py

import os
import tempfile
import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        config_content = '''[embed]
EMBED_TYPE = "openai"
MAX_LENGTH = 64
IS_ASYNC = false

[embed.openai]
MODEL = "BAAI/bge-m3"
BASE_URL = "https://api.openai.com/v1"
API_KEY = ["test-key"]

[embed.ollama]
MODEL = "bge-m3:latest"
BASE_URL = "http://localhost:11434"
API_KEY = ["ollama"]

[texiv.chunk]
stopwords_path = ""

[texiv.similarity]
MTHD = "cosine"

[texiv.filter]
VALVE_TYPE = "value"
valve = 0.618
'''
        f.write(config_content)
        f.flush()
        yield f.name
        # Cleanup after test
        if os.path.exists(f.name):
            os.unlink(f.name)

@pytest.fixture
def mock_config_paths(temp_config_file):
    """Mock configuration paths for testing"""
    def mock_path():
        return temp_config_file
    
    return mock_path

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch, temp_config_file):
    """Setup test environment"""
    # Mock the config path
    from texiv.cli import CLI
    from texiv.config import Config
    
    original_config_path = CLI.CONFIG_FILE_PATH
    original_is_exist = CLI.IS_EXIST_CONFIG_FILE
    
    CLI.CONFIG_FILE_PATH = temp_config_file
    CLI.IS_EXIST_CONFIG_FILE = True
    Config.CONFIG_FILE_PATH = temp_config_file
    
    yield
    
    # Restore original values
    CLI.CONFIG_FILE_PATH = original_config_path
    CLI.IS_EXIST_CONFIG_FILE = original_is_exist
    Config.CONFIG_FILE_PATH = original_config_path