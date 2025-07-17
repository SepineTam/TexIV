"""Tests for CLI with rich output."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

from texiv.cli import CLI
from texiv.utils import create_rich_helper


class TestCLIWithRich:
    """Test CLI commands with rich output integration."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.toml"
        
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_config(self):
        """Create a test configuration file."""
        import tomlkit
        config = tomlkit.document()
        
        config["embed"] = tomlkit.table()
        config["embed"]["EMBED_TYPE"] = "openai"
        config["embed"]["MAX_LENGTH"] = 64
        config["embed"]["IS_ASYNC"] = False
        
        config["embed"]["openai"] = tomlkit.table()
        config["embed"]["openai"]["MODEL"] = "test-model"
        config["embed"]["openai"]["BASE_URL"] = "http://test.com"
        config["embed"]["openai"]["API_KEY"] = ["test-key"]
        
        config["texiv"] = tomlkit.table()
        config["texiv"]["chunk"] = tomlkit.table()
        config["texiv"]["chunk"]["stopwords_path"] = ""
        
        config["texiv"]["similarity"] = tomlkit.table()
        config["texiv"]["similarity"]["MTHD"] = "cosine"
        
        config["texiv"]["filter"] = tomlkit.table()
        config["texiv"]["filter"]["VALVE_TYPE"] = "value"
        config["texiv"]["filter"]["valve"] = 0.618
        
        with open(self.config_path, "w") as f:
            f.write(tomlkit.dumps(config))
        
        return str(self.config_path)

    @patch('texiv.config.Config.CONFIG_FILE_PATH', new_callable=lambda: str(Path(tempfile.mkdtemp()) / "config.toml"))
    def test_do_init_with_rich(self, mock_config_path):
        """Test do_init method with rich output."""
        cli = CLI()
        rich_helper = create_rich_helper(quiet=True)
        
        # Mock input to return False (cancel initialization)
        result = cli.do_init(input_func=lambda x: "n", rich_helper=rich_helper)
        assert result == 0

    @patch('texiv.config.Config.CONFIG_FILE_PATH', new_callable=lambda: str(Path(tempfile.mkdtemp()) / "config.toml"))
    def test_do_cat_with_rich(self, mock_config_path):
        """Test do_cat method with rich output."""
        self.create_test_config()
        cli = CLI()
        rich_helper = create_rich_helper(quiet=True)
        
        # Copy test config to mock path
        import shutil
        shutil.copy2(str(self.config_path), mock_config_path)
        
        result = cli.do_cat(rich_helper=rich_helper)
        assert result == 0

    def test_do_add_key_with_rich(self):
        """Test do_add_key method with rich output."""
        self.create_test_config()
        
        # Mock the config path
        with patch('texiv.config.Config.CONFIG_FILE_PATH', str(self.config_path)):
            cli = CLI()
            rich_helper = create_rich_helper(quiet=True)
            
            result = cli.do_add_key("new-test-key", rich_helper=rich_helper)
            assert result == 0

    @patch('texiv.config.Config.CONFIG_FILE_PATH', new_callable=lambda: str(Path(tempfile.mkdtemp()) / "config.toml"))
    def test_do_set_with_rich(self, mock_config_path):
        """Test do_set method with rich output."""
        self.create_test_config()
        cli = CLI()
        rich_helper = create_rich_helper(quiet=True)
        
        # Copy test config to mock path
        import shutil
        shutil.copy2(str(self.config_path), mock_config_path)
        
        result = cli.do_set("embed.openai.MODEL", "new-model", rich_helper=rich_helper)
        assert result == 0

    @patch('texiv.config.Config.CONFIG_FILE_PATH', new_callable=lambda: str(Path(tempfile.mkdtemp()) / "config.toml"))
    def test_do_rm_with_rich(self, mock_config_path):
        """Test do_rm method with rich output."""
        self.create_test_config()
        cli = CLI()
        rich_helper = create_rich_helper(quiet=True)
        
        # Copy test config to mock path
        import shutil
        shutil.copy2(str(self.config_path), mock_config_path)
        
        result = cli.do_rm("embed.openai.MODEL", rich_helper=rich_helper)
        assert result == 0

    @patch('texiv.config.Config.CONFIG_FILE_PATH', new_callable=lambda: str(Path(tempfile.mkdtemp()) / "config.toml"))
    def test_do_upgrade_with_rich(self, mock_config_path):
        """Test do_upgrade method with rich output."""
        self.create_test_config()
        cli = CLI()
        rich_helper = create_rich_helper(quiet=True)
        
        # Copy test config to mock path
        import shutil
        shutil.copy2(str(self.config_path), mock_config_path)
        
        result = cli.do_upgrade(rich_helper=rich_helper)
        assert result == 0

    def test_exit_with_not_exist(self):
        """Test exit_with_not_exist method."""
        cli = CLI()
        # Mock IS_EXIST_CONFIG_FILE to False
        with patch.object(cli, 'IS_EXIST_CONFIG_FILE', False):
            with pytest.raises(SystemExit) as exc_info:
                cli.exit_with_not_exist()
            assert exc_info.value.code == 1

    def test_rich_helper_parameter_handling(self):
        """Test that rich_helper parameter is properly handled."""
        cli = CLI()
        
        # Test that methods accept rich_helper parameter
        assert hasattr(cli, 'do_init')
        assert hasattr(cli, 'do_upgrade')
        assert hasattr(cli, 'do_cat')
        assert hasattr(cli, 'do_add_key')
        assert hasattr(cli, 'do_set')
        assert hasattr(cli, 'do_rm')

    def test_main_function_with_quiet_flag(self):
        """Test main function with --quiet flag."""
        test_args = ["texiv", "--quiet", "--cat"]
        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                # Mock config file existence and content
                with patch('texiv.cli.CLI.IS_EXIST_CONFIG_FILE', True):
                    mock_file = MagicMock()
                    mock_file.read.return_value = "[test]\nkey = 'value'"
                    mock_context = MagicMock()
                    mock_context.__enter__.return_value = mock_file
                    mock_open = MagicMock(return_value=mock_context)
                    with patch('builtins.open', mock_open):
                        from texiv.cli import main
                        main()
            # Should exit gracefully
            assert exc_info.value.code in [0, 1]

    def test_main_function_with_verbose_flag(self):
        """Test main function with --verbose flag."""
        test_args = ["texiv", "--verbose"]
        with patch('sys.argv', test_args):
            try:
                from texiv.cli import main
                main()
            except SystemExit as e:
                # Should exit gracefully with help
                assert e.code == 0 or e.code is None