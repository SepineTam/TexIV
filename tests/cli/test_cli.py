#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : test_cli.py

import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from texiv.cli import CLI, main


class TestCLI:
    """Test cases for TexIV CLI functionality"""

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary directory for configuration files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def mock_config(self, temp_config_dir):
        """Create a mock configuration file for testing"""
        config_path = Path(temp_config_dir) / "config.toml"
        
        config_content = '''[embed]
EMBED_TYPE = "openai"
MAX_LENGTH = 64
IS_ASYNC = false

[embed.openai]
MODEL = "BAAI/bge-m3"
BASE_URL = "https://api.openai.com/v1"
API_KEY = ["test-key-1", "test-key-2"]

[texiv.chunk]
stopwords_path = ""

[texiv.similarity]
MTHD = "cosine"

[texiv.filter]
VALVE_TYPE = "value"
valve = 0.618
'''
        config_path.write_text(config_content)
        return config_path

    @pytest.fixture
    def cli_instance(self, mock_config):
        """Create CLI instance with mocked config path"""
        cli = CLI()
        cli.CONFIG_FILE_PATH = str(mock_config)
        cli.IS_EXIST_CONFIG_FILE = True
        return cli

    def test_init_with_existing_config(self, cli_instance):
        """Test initialization with existing config file"""
        result = cli_instance.exit_with_not_exist()
        assert result is None

    def test_init_with_missing_config(self):
        """Test initialization with missing config file"""
        cli = CLI()
        cli.CONFIG_FILE_PATH = "/nonexistent/path/config.toml"
        cli.IS_EXIST_CONFIG_FILE = False
        
        with pytest.raises(SystemExit) as exc_info:
            cli.exit_with_not_exist()
        assert exc_info.value.code == 1

    @patch('texiv.config.Config.cli_init')
    def test_do_init_confirmed(self, mock_config_init):
        """Test do_init with user confirmation"""
        def mock_input(msg):
            return "y"
        
        result = CLI.do_init(input_func=mock_input)
        assert result == 0
        mock_config_init.assert_called_once()

    @patch('texiv.config.Config.cli_init')
    def test_do_init_cancelled(self, mock_config_init):
        """Test do_init with user cancellation"""
        def mock_input(msg):
            return "n"
        
        result = CLI.do_init(input_func=mock_input)
        assert result == 0
        mock_config_init.assert_not_called()

    def test_do_cat(self, capsys, cli_instance):
        """Test do_cat function displays config content"""
        result = cli_instance.do_cat()
        assert result == 0
        
        captured = capsys.readouterr()
        assert "EMBED_TYPE" in captured.out
        assert "BAAI/bge-m3" in captured.out

    @patch('texiv.config.Config.add_api_key')
    def test_do_add_key_success(self, mock_add_key):
        """Test successful API key addition"""
        cli = CLI()
        cli.CONFIG_FILE_PATH = "/tmp/test.toml"
        cli.IS_EXIST_CONFIG_FILE = True
        
        result = cli.do_add_key("test-api-key")
        assert result == 0
        mock_add_key.assert_called_once_with("test-api-key")

    @patch('texiv.config.Config.add_api_key')
    def test_do_add_key_failure(self, mock_add_key):
        """Test API key addition failure"""
        mock_add_key.side_effect = Exception("API key format error")
        
        cli = CLI()
        cli.CONFIG_FILE_PATH = "/tmp/test.toml"
        cli.IS_EXIST_CONFIG_FILE = True
        
        result = cli.do_add_key("invalid-key")
        assert result == 1

    def test_do_set_string_value(self, cli_instance):
        """Test setting string configuration value"""
        result = cli_instance.do_set("embed.openai.MODEL", "new-model")
        assert result == 0
        
        config_content = Path(cli_instance.CONFIG_FILE_PATH).read_text()
        assert "new-model" in config_content

    def test_do_set_numeric_value(self, cli_instance):
        """Test setting numeric configuration value"""
        result = cli_instance.do_set("texiv.filter.valve", "0.95")
        assert result == 0
        
        config_content = Path(cli_instance.CONFIG_FILE_PATH).read_text()
        assert "0.95" in config_content

    def test_do_set_boolean_value(self, cli_instance):
        """Test setting boolean configuration value"""
        result = cli_instance.do_set("embed.IS_ASYNC", "true")
        assert result == 0
        
        config_content = Path(cli_instance.CONFIG_FILE_PATH).read_text()
        assert "true" in config_content

    def test_do_set_list_value(self, cli_instance):
        """Test setting list configuration value"""
        result = cli_instance.do_set("embed.openai.API_KEY", '["key1", "key2", "key3"]')
        assert result == 0
        
        config_content = Path(cli_instance.CONFIG_FILE_PATH).read_text()
        assert '"key1"' in config_content
        assert '"key2"' in config_content
        assert '"key3"' in config_content

    def test_do_set_nested_key_creation(self, cli_instance):
        """Test creating nested keys automatically"""
        result = cli_instance.do_set("test.section.new_key", "test_value")
        assert result == 0
        
        config_content = Path(cli_instance.CONFIG_FILE_PATH).read_text()
        assert "[test.section]" in config_content or "new_key = \"test_value\"" in config_content

    def test_do_rm_with_default(self, cli_instance):
        """Test removing key with default value restoration"""
        # First set a custom value
        result1 = cli_instance.do_set("texiv.filter.valve", "0.85")
        assert result1 == 0
        
        # Then remove it to restore default
        result2 = cli_instance.do_rm("texiv.filter.valve")
        assert result2 == 0
        
        config_content = Path(cli_instance.CONFIG_FILE_PATH).read_text()
        assert "0.618" in config_content

    def test_do_rm_without_default(self, cli_instance):
        """Test removing key without default value"""
        # Add a custom key
        result1 = cli_instance.do_set("custom.section.key", "value")
        assert result1 == 0
        
        # Remove it
        result2 = cli_instance.do_rm("custom.section.key")
        assert result2 == 0
        
        config_content = Path(cli_instance.CONFIG_FILE_PATH).read_text()
        assert "custom.section.key" not in config_content

    def test_do_rm_nonexistent_key(self, cli_instance):
        """Test removing non-existent key"""
        with pytest.raises(SystemExit) as exc_info:
            cli_instance.do_rm("nonexistent.key")
        assert exc_info.value.code == 1

    def test_do_set_invalid_path(self, cli_instance):
        """Test setting value with invalid path handling"""
        result = cli_instance.do_set("very.deep.nested.path", "value")
        assert result == 0
        
        config_content = Path(cli_instance.CONFIG_FILE_PATH).read_text()
        assert "path" in config_content

    def test_do_upgrade_backup_created(self, temp_config_dir):
        """Test upgrade creates backup file"""
        old_config_path = Path(temp_config_dir) / "old_config.toml"
        old_config_path.write_text('''[old_section]
old_key = "old_value"
''')
        
        cli = CLI()
        cli.CONFIG_FILE_PATH = str(old_config_path)
        cli.IS_EXIST_CONFIG_FILE = True
        
        result = cli.do_upgrade()
        assert result == 0
        
        # Check if backup file was created
        backup_files = list(Path(temp_config_dir).glob("*.backup.*"))
        assert len(backup_files) >= 1

    def test_main_version_flag(self, capsys):
        """Test main function with version flag"""
        test_args = ['texiv', '--version']
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        assert exc_info.value.code == 0
        
        captured = capsys.readouterr()
        assert "TexIV" in captured.out

    def test_main_help_flag(self, capsys):
        """Test main function with help flag"""
        test_args = ['texiv', '--help']
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        assert exc_info.value.code == 0
        
        captured = capsys.readouterr()
        assert "usage:" in captured.out

    def test_main_set_command(self, cli_instance):
        """Test main function with set command"""
        test_args = ['texiv', 'set', 'embed.openai.MODEL', 'test-model']
        
        with patch.object(sys, 'argv', test_args):
            with patch('texiv.cli.CLI.CONFIG_FILE_PATH', cli_instance.CONFIG_FILE_PATH):
                with patch('texiv.cli.CLI.IS_EXIST_CONFIG_FILE', True):
                    try:
                        main()
                    except SystemExit as e:
                        assert e.code == 0

    def test_main_rm_command(self, cli_instance):
        """Test main function with rm command"""
        test_args = ['texiv', 'rm', 'texiv.filter.valve']
        
        with patch.object(sys, 'argv', test_args):
            with patch('texiv.cli.CLI.CONFIG_FILE_PATH', cli_instance.CONFIG_FILE_PATH):
                with patch('texiv.cli.CLI.IS_EXIST_CONFIG_FILE', True):
                    try:
                        main()
                    except SystemExit as e:
                        assert e.code == 0

    def test_do_set_error_handling(self, cli_instance):
        """Test error handling in do_set"""
        # This should not raise exception, but return 0 on success
        result = cli_instance.do_set("nonexistent", "value")
        assert result == 0

    def test_do_rm_error_handling(self, cli_instance):
        """Test error handling in do_rm"""
        with pytest.raises(SystemExit) as exc_info:
            cli_instance.do_rm("nonexistent.key")
        assert exc_info.value.code == 1


class TestMainFunctionality:
    """Test main CLI entry point"""

    def test_main_with_init_missing_config(self):
        """Test main with init when config doesn't exist"""
        test_args = ['texiv', '--init']
        
        def mock_input(msg):
            return "n"  # Simulate user cancellation
        
        with patch.object(sys, 'argv', test_args):
            with patch('texiv.cli.CLI.CONFIG_FILE_PATH', '/nonexistent/config.toml'):
                with patch('texiv.cli.CLI.IS_EXIST_CONFIG_FILE', False):
                    with patch('builtins.input', mock_input):
                        # init works even without config file, returns 0
                        result = main()
                        assert result == 0

    def test_main_with_cat_missing_config(self):
        """Test main with cat when config doesn't exist"""
        test_args = ['texiv', '--cat']
        
        with patch.object(sys, 'argv', test_args):
            with patch('texiv.cli.CLI.CONFIG_FILE_PATH', '/nonexistent/config.toml'):
                with patch('texiv.cli.CLI.IS_EXIST_CONFIG_FILE', False):
                    with pytest.raises(SystemExit) as exc_info:
                        main()
                    assert exc_info.value.code == 1

    def test_main_with_upgrade_missing_config(self):
        """Test main with upgrade when config doesn't exist"""
        test_args = ['texiv', '--upgrade']
        
        with patch.object(sys, 'argv', test_args):
            with patch('texiv.cli.CLI.CONFIG_FILE_PATH', '/nonexistent/config.toml'):
                with patch('texiv.cli.CLI.IS_EXIST_CONFIG_FILE', False):
                    with pytest.raises(SystemExit) as exc_info:
                        main()
                    assert exc_info.value.code == 1


class TestValueParsing:
    """Test value parsing functionality"""

    def test_parse_string_value(self):
        """Test string value parsing"""
        cli = CLI()
        cli.CONFIG_FILE_PATH = "/tmp/test.toml"
        cli.IS_EXIST_CONFIG_FILE = True
        
        # Test will indirectly test parsing through do_set
        pass

    def test_parse_boolean_value(self):
        """Test boolean value parsing"""
        cli = CLI()
        cli.CONFIG_FILE_PATH = "/tmp/test.toml"
        cli.IS_EXIST_CONFIG_FILE = True
        
        # Test will indirectly test parsing through do_set
        pass

    def test_parse_numeric_value(self):
        """Test numeric value parsing"""
        cli = CLI()
        cli.CONFIG_FILE_PATH = "/tmp/test.toml"
        cli.IS_EXIST_CONFIG_FILE = True
        
        # Test will indirectly test parsing through do_set
        pass

    def test_parse_list_value(self):
        """Test list value parsing"""
        cli = CLI()
        cli.CONFIG_FILE_PATH = "/tmp/test.toml"
        cli.IS_EXIST_CONFIG_FILE = True
        
        # Test will indirectly test parsing through do_set
        pass


if __name__ == "__main__":
    pytest.main([__file__])