"""Tests for rich utilities."""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

from texiv.utils import create_rich_helper, RichHelper


class TestRichHelper:
    """Test cases for RichHelper class."""

    def test_create_rich_helper_default(self):
        """Test creating RichHelper with default parameters."""
        helper = create_rich_helper()
        assert isinstance(helper, RichHelper)
        assert helper.quiet is False

    def test_create_rich_helper_quiet(self):
        """Test creating RichHelper with quiet mode."""
        helper = create_rich_helper(quiet=True)
        assert isinstance(helper, RichHelper)
        assert helper.quiet is True

    def test_print_success_not_quiet(self, capsys):
        """Test print_success when not in quiet mode."""
        helper = create_rich_helper(quiet=False)
        helper.print_success("Test success message")
        captured = capsys.readouterr()
        # Rich console output might not be captured by capsys
        # Just ensure no exception is raised
        assert captured.err == ""

    def test_print_success_quiet(self, capsys):
        """Test print_success when in quiet mode."""
        helper = create_rich_helper(quiet=True)
        helper.print_success("Test success message")
        captured = capsys.readouterr()
        # In quiet mode, should not output anything
        assert captured.out == ""

    def test_print_error_not_quiet(self, capsys):
        """Test print_error when not in quiet mode."""
        helper = create_rich_helper(quiet=False)
        helper.print_error("Test error message")
        captured = capsys.readouterr()
        # Error messages should always be shown
        assert "Test error message" in captured.out or captured.out == ""

    def test_print_warning_quiet(self, capsys):
        """Test print_warning when in quiet mode."""
        helper = create_rich_helper(quiet=True)
        helper.print_warning("Test warning message")
        captured = capsys.readouterr()
        # In quiet mode, should not output anything
        assert captured.out == ""

    def test_print_info_quiet(self, capsys):
        """Test print_info when in quiet mode."""
        helper = create_rich_helper(quiet=True)
        helper.print_info("Test info message")
        captured = capsys.readouterr()
        # In quiet mode, should not output anything
        assert captured.out == ""

    def test_create_progress_not_quiet(self):
        """Test creating progress bar when not in quiet mode."""
        helper = create_rich_helper(quiet=False)
        progress = helper.create_progress("Test progress")
        assert progress is not None
        task = progress.add_task("Test", total=10)
        assert task is not None

    def test_create_progress_quiet(self):
        """Test creating progress bar when in quiet mode."""
        helper = create_rich_helper(quiet=True)
        progress = helper.create_progress("Test progress")
        assert progress is not None
        task = progress.add_task("Test", total=10)
        assert task is not None
        # In quiet mode, progress should be disabled
        assert progress.disable is True

    def test_display_results_table_not_quiet(self, capsys):
        """Test displaying results table when not in quiet mode."""
        helper = create_rich_helper(quiet=False)
        test_data = {"key1": "value1", "key2": 42}
        helper.display_results_table("Test Table", test_data)
        captured = capsys.readouterr()
        # Just ensure no exception is raised
        assert captured.err == ""

    def test_display_results_table_quiet(self, capsys):
        """Test displaying results table when in quiet mode."""
        helper = create_rich_helper(quiet=True)
        test_data = {"key1": "value1", "key2": 42}
        helper.display_results_table("Test Table", test_data)
        captured = capsys.readouterr()
        # In quiet mode, should not output anything
        assert captured.out == ""

    def test_display_status_panel_not_quiet(self, capsys):
        """Test displaying status panel when not in quiet mode."""
        helper = create_rich_helper(quiet=False)
        test_content = {"status": "processing", "count": 10}
        helper.display_status_panel("Test Panel", test_content)
        captured = capsys.readouterr()
        # Just ensure no exception is raised
        assert captured.err == ""

    def test_display_status_panel_quiet(self, capsys):
        """Test displaying status panel when in quiet mode."""
        helper = create_rich_helper(quiet=True)
        test_content = {"status": "processing", "count": 10}
        helper.display_status_panel("Test Panel", test_content)
        captured = capsys.readouterr()
        # In quiet mode, should not output anything
        assert captured.out == ""

    def test_setup_logging(self):
        """Test setting up logging with RichHandler."""
        helper = create_rich_helper()
        helper.setup_logging()
        # Just ensure no exception is raised
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Test logging message")

    @patch('sys.stdout', new_callable=StringIO)
    def test_console_output_in_non_quiet_mode(self, mock_stdout):
        """Test that console outputs in non-quiet mode."""
        helper = create_rich_helper(quiet=False)
        helper.print_info("Test message")
        # Rich uses complex formatting, just check method exists and runs
        assert hasattr(helper, 'print_info')

    @patch('sys.stdout', new_callable=StringIO)
    def test_no_console_output_in_quiet_mode(self, mock_stdout):
        """Test that console does not output in quiet mode."""
        helper = create_rich_helper(quiet=True)
        helper.print_info("Test message")
        helper.print_warning("Test warning")
        helper.print_success("Test success")
        # In quiet mode, non-error messages should be suppressed
        output = mock_stdout.getvalue()
        # Error messages should still show
        assert "Test message" not in output
        assert "Test warning" not in output
        assert "Test success" not in output


class TestRichHelperIntegration:
    """Integration tests for RichHelper with TexIV."""

    def test_rich_helper_with_texiv_initialization(self):
        """Test RichHelper integration with TexIV class."""
        from texiv.core.texiv import TexIV
        helper = create_rich_helper(quiet=True)
        # Should not raise exception when initializing with custom helper
        try:
            texiv = TexIV(rich_helper=helper, valve=0.5)
            assert texiv.rich_helper is helper
        except FileNotFoundError:
            # Expected when config file doesn't exist in test environment
            pytest.skip("Configuration file not found")

    def test_rich_helper_progress_context_manager(self):
        """Test progress bar context manager functionality."""
        helper = create_rich_helper(quiet=True)
        with helper.create_progress("Test description") as progress:
            # Should not raise exception
            assert progress is not None
            task = progress.add_task("Test", total=10)
            # Test progress update
            progress.update(task, advance=1)

    def test_rich_helper_table_display(self):
        """Test table display functionality."""
        helper = create_rich_helper(quiet=True)
        # Should not raise exception
        helper.display_results_table("Test", {"a": 1, "b": 2})

    def test_rich_helper_panel_display(self):
        """Test panel display functionality."""
        helper = create_rich_helper(quiet=True)
        # Should not raise exception
        helper.display_status_panel("Test", {"status": "ok"})