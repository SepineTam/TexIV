#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : __init__.py

import argparse
import logging
import sys

from rich.console import Console
from rich.panel import Panel

from .. import __version__
from ..config import Config
from ..core.utils import yes_or_no
from ..utils import create_rich_helper, print_colored


def main():
    cli = CLI()
    parser = argparse.ArgumentParser(description="TexIV CLI")

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"TexIV {__version__}",
        help="Show the program's version number"
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress all output except errors"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output with rich formatting"
    )

    parser.add_argument(
        "-i", "--init",
        action="store_true",
        help="Initialize TexIV configuration"
    )

    parser.add_argument(
        "-u", "--upgrade",
        action="store_true",
        help="Upgrade TexIV configuration from old one"
    )

    parser.add_argument(
        "--cat",
        action="store_true",
        help="Show TexIV configuration"
    )

    # Add sub parsers for set and rm commands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands'
    )

    # Add new api_key
    add_key_parser = subparsers.add_parser(
        "add",
        help="Add new API KEY for embedding service"
    )
    add_key_parser.add_argument(
        "key",
        help="New API KEY"
    )

    # Add set sub parser
    set_parser = subparsers.add_parser(
        'set',
        help='Set configuration value'
    )
    set_parser.add_argument(
        'key_path',
        help='Configuration key path'
    )
    set_parser.add_argument(
        'value',
        help='Configuration value'
    )

    # Add rm sub parser
    rm_parser = subparsers.add_parser(
        'rm',
        help='Remove configuration key replaced with default value'
    )
    rm_parser.add_argument(
        'key_path',
        help='Configuration key path to remove'
    )

    args = parser.parse_args()

    # Create rich helper with quiet mode support
    rich_helper = create_rich_helper(quiet=args.quiet)

    if args.init:
        return cli.do_init(input_func=input, rich_helper=rich_helper)
    if args.upgrade:
        return cli.do_upgrade(rich_helper=rich_helper)
    if args.cat:
        return cli.do_cat(rich_helper=rich_helper)
    if args.command == 'add':
        return cli.do_add_key(key=args.key, rich_helper=rich_helper)
    if args.command == 'set':
        return cli.do_set(
            key_path=args.key_path,
            value=args.value,
            rich_helper=rich_helper)
    if args.command == 'rm':
        return cli.do_rm(key_path=args.key_path, rich_helper=rich_helper)

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        rich_helper.print_info("Welcome to TexIV!")
        parser.print_help()

    return 0


class CLI:
    CONFIG_FILE_PATH = Config.CONFIG_FILE_PATH
    IS_EXIST_CONFIG_FILE = Config.is_exist()

    def __init__(self):
        banner = """
████████╗███████╗██╗  ██╗██╗██╗   ██╗
╚══██╔══╝██╔════╝╚██╗██╔╝██║██║   ██║
   ██║   █████╗   ╚███╔╝ ██║██║   ██║
   ██║   ██╔══╝   ██╔██╗ ██║╚██╗ ██╔╝
   ██║   ███████╗██╔╝ ██╗██║ ╚████╔╝
   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝
        """
        separator = "━" * 40
        print_colored(banner, 'magenta')
        print_colored(separator, 'blue')
        print_colored("      Transforming text as IV.      ", 'bold')
        print_colored(separator, 'blue')
        print()
        print_colored(f"Version {__version__}", 'green')
        print_colored("Type 'help' for available commands", 'yellow')
        print()

    def exit_with_not_exist(self):
        """
        Check whether existing the config file.

        If existed, do nothing;
        If not existed, exit the program with message.
        """
        if self.IS_EXIST_CONFIG_FILE:
            return None
        else:
            logging.warning("There is no existing config file.")
            sys.exit(1)

    @staticmethod
    def do_init(input_func=None, rich_helper=None):
        if rich_helper is None:
            rich_helper = create_rich_helper()

        rich_helper.print_warning(
            "You are initializing TexIV configuration...\n"
            "You must know that initializing will overwrite your current configuration.")
        flag = yes_or_no("Do you want to continue?", input_func=input_func)
        if flag:
            with rich_helper.create_progress("Initializing configuration") as progress:
                task = progress.add_task("Initializing", total=1)
                Config.cli_init()
                progress.update(task, completed=1)
            rich_helper.print_success(
                "Configuration initialized successfully!")
        return 0

    def do_upgrade(self, rich_helper=None):
        """
        Upgrade configuration from old versions to new format using template merging.
        Preserves existing settings and adds missing sections with defaults.
        """
        if rich_helper is None:
            rich_helper = create_rich_helper()

        self.exit_with_not_exist()

        try:
            import shutil
            from datetime import datetime
            from pathlib import Path

            import tomlkit
            import tomllib

            config_path = Path(self.CONFIG_FILE_PATH)
            backup_path = config_path.with_suffix(
                f'.toml.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            )

            rich_helper.print_info("Starting configuration upgrade...")

            with rich_helper.create_progress("Creating backup") as progress:
                task = progress.add_task("Creating backup", total=1)
                shutil.copy2(config_path, backup_path)
                progress.update(task, completed=1)

            rich_helper.print_success(
                f"Configuration backup created at: {backup_path}")

            # Load current config
            with open(config_path, "rb") as f:
                user_config = tomllib.load(f)

            # Define template with latest structure
            template = tomlkit.document()

            # Embed section template
            template["embed"] = tomlkit.table()
            template["embed"]["EMBED_TYPE"] = "openai"
            template["embed"]["MAX_LENGTH"] = 64
            template["embed"]["IS_ASYNC"] = False

            template["embed"]["openai"] = tomlkit.table()
            template["embed"]["openai"]["MODEL"] = "BAAI/bge-m3"
            template["embed"]["openai"]["BASE_URL"] = "https://api.openai.com/v1"
            template["embed"]["openai"]["API_KEY"] = ["your-api-key-here"]

            template["embed"]["ollama"] = tomlkit.table()
            template["embed"]["ollama"]["MODEL"] = "bge-m3:latest"
            template["embed"]["ollama"]["BASE_URL"] = "http://localhost:11434"
            template["embed"]["ollama"]["API_KEY"] = ["ollama"]

            # Texiv section template
            template["texiv"] = tomlkit.table()
            template["texiv"]["chunk"] = tomlkit.table()
            template["texiv"]["chunk"]["stopwords_path"] = ""

            template["texiv"]["similarity"] = tomlkit.table()
            template["texiv"]["similarity"]["MTHD"] = "cosine"

            template["texiv"]["filter"] = tomlkit.table()
            template["texiv"]["filter"]["VALVE_TYPE"] = "value"
            template["texiv"]["filter"]["valve"] = 0.618

            # Merge user config with template (user config takes precedence)
            def deep_merge(target, source):
                """Recursively merge source into target, preserving user values"""
                for key, value in source.items():
                    if key not in target:
                        target[key] = value
                    elif isinstance(value, dict) and isinstance(target[key], dict):
                        deep_merge(target[key], value)
                    # User values take precedence, skip existing keys

            with rich_helper.create_progress("Merging configuration") as progress:
                task = progress.add_task("Merging configuration", total=1)
                # Create merged config
                merged_config = tomlkit.document()
                deep_merge(merged_config, template)
                deep_merge(merged_config, user_config)
                progress.update(task, completed=1)

            # Handle API_KEY type conversion (ensure it's always a list)
            for service in ["openai", "ollama"]:
                if service in merged_config["embed"]:
                    api_keys = merged_config["embed"][service]["API_KEY"]
                    if isinstance(api_keys, str):
                        merged_config["embed"][service]["API_KEY"] = [api_keys]
                    elif not isinstance(api_keys, list):
                        merged_config["embed"][service]["API_KEY"] = [
                            str(api_keys)]

            with rich_helper.create_progress("Writing upgraded configuration") as progress:
                task = progress.add_task("Writing configuration", total=1)
                # Write upgraded configuration
                with open(config_path, "w") as f:
                    f.write(tomlkit.dumps(merged_config))
                progress.update(task, completed=1)

            rich_helper.print_success("Configuration successfully upgraded!")

            upgrade_summary = {
                "Backup Location": str(backup_path),
                "Status": "✅ Completed",
                "Changes": "Configuration structure updated",
                "Preserved": "All existing settings",
                "Added": "Missing sections with defaults",
                "Format": "API_KEY values normalized to list"
            }
            rich_helper.display_results_table(
                "Upgrade Summary", upgrade_summary)

            return 0

        except Exception as e:
            logging.error(f"Failed to upgrade configuration: {e}")
            rich_helper.print_error(f"Error during upgrade: {e}")
            rich_helper.print_warning(
                "Your original configuration remains unchanged.")
            return 1

    def do_cat(self, rich_helper=None):
        self.exit_with_not_exist()
        if rich_helper is None:
            rich_helper = create_rich_helper()

        # Show the config file content in a panel
        with open(self.CONFIG_FILE_PATH, "r") as f:
            content = f.read()

        rich_helper.console.print(Panel(
            content,
            title="TexIV Configuration",
            title_align="left",
            border_style="green",
            expand=False
        ))
        return 0

    def do_add_key(self, key, rich_helper=None):
        self.exit_with_not_exist()
        if rich_helper is None:
            rich_helper = create_rich_helper()

        try:
            with rich_helper.create_progress("Adding API key") as progress:
                task = progress.add_task("Adding API key", total=1)
                Config().add_api_key(key)
                progress.update(task, completed=1)

            rich_helper.print_success("API key added successfully!")
            return 0
        except Exception as e:
            logging.error(f"Failed to add API key: {e}")
            rich_helper.print_error(f"Failed to add API key: {e}")
            return 1

    def do_set(self, key_path, value, rich_helper=None):
        """
        Set a configuration value by key path.
        Supports dot notation like: embed.openai.MODEL or texiv.filter.valve
        """
        self.exit_with_not_exist()
        if rich_helper is None:
            rich_helper = create_rich_helper()

        try:
            import ast

            import tomlkit

            config_path = self.CONFIG_FILE_PATH

            # Load current config
            with open(config_path, "rb") as f:
                config = tomlkit.load(f)

            # Parse the value (handle numbers, booleans, strings, and lists)
            def parse_value(val_str):
                """Parse string value to appropriate type"""
                val_str = val_str.strip()

                # Handle list format: ["item1", "item2"]
                if val_str.startswith('[') and val_str.endswith(']'):
                    try:
                        parsed = ast.literal_eval(val_str)
                        if isinstance(parsed, list):
                            return parsed
                    except (ValueError, SyntaxError):
                        return [item.strip().strip('"\'')
                                for item in val_str[1:-1].split(',')]

                # Handle boolean values
                if val_str.lower() in ('true', 'false'):
                    return val_str.lower() == 'true'

                # Handle numeric values
                try:
                    if '.' in val_str:
                        return float(val_str)
                    return int(val_str)
                except ValueError:
                    pass

                # Handle string values (remove quotes if present)
                return val_str.strip('"\'')

            parsed_value = parse_value(value)

            # Split key path and navigate to the target
            keys = key_path.split('.')
            current = config

            # Navigate to the parent of the target key
            for key in keys[:-1]:
                if key not in current:
                    current[key] = tomlkit.table()
                current = current[key]

            # Set the final key
            final_key = keys[-1]
            current[final_key] = parsed_value

            with rich_helper.create_progress("Saving configuration") as progress:
                task = progress.add_task("Saving configuration", total=1)
                # Write back to file
                with open(config_path, "w") as f:
                    f.write(tomlkit.dumps(config))
                progress.update(task, completed=1)

            rich_helper.print_success(
                f"Successfully set {key_path} = {parsed_value}")
            return 0

        except Exception as e:
            logging.error(f"Failed to set configuration value: {e}")
            rich_helper.print_error(f"Error setting {key_path}: {e}")
            return 1

    def do_rm(self, key_path, rich_helper=None):
        """
        Remove a configuration key and replace with default value.
        Supports dot notation like: embed.openai.MODEL or texiv.filter.valve
        """
        self.exit_with_not_exist()
        if rich_helper is None:
            rich_helper = create_rich_helper()

        try:
            import tomlkit

            config_path = self.CONFIG_FILE_PATH

            # Load current config
            with open(config_path, "rb") as f:
                config = tomlkit.load(f)

            # Split key path and navigate to the target
            keys = key_path.split('.')
            current = config

            # Navigate to the parent of the target key
            for key in keys[:-1]:
                if key not in current:
                    rich_helper.print_error(
                        f"Key path {key_path} not found in configuration")
                    sys.exit(1)
                current = current[key]

            # Remove the final key
            final_key = keys[-1]
            if final_key not in current:
                rich_helper.print_error(
                    f"Key {final_key} not found in {'.'.join(keys[:-1])}")
                sys.exit(1)

            # Get the default value based on key path
            def get_default_value(keys):
                """Get default value for a given key path"""
                defaults = {
                    'embed.EMBED_TYPE': 'openai',
                    'embed.MAX_LENGTH': 64,
                    'embed.IS_ASYNC': False,
                    'embed.openai.MODEL': 'BAAI/bge-m3',
                    'embed.openai.BASE_URL': 'https://api.openai.com/v1',
                    'embed.openai.API_KEY': ['your-api-key-here'],
                    'embed.ollama.MODEL': 'bge-m3:latest',
                    'embed.ollama.BASE_URL': 'http://localhost:11434',
                    'embed.ollama.API_KEY': ['ollama'],
                    'texiv.chunk.stopwords_path': '',
                    'texiv.similarity.MTHD': 'cosine',
                    'texiv.filter.VALVE_TYPE': 'value',
                    'texiv.filter.valve': 0.618
                }
                return defaults.get('.'.join(keys), None)

            default_value = get_default_value(keys)

            with rich_helper.create_progress("Removing configuration key") as progress:
                task = progress.add_task("Removing configuration key", total=1)
                if default_value is None:
                    # If no default exists, just remove the key
                    del current[final_key]
                    message = f"Successfully removed {key_path} (no default value)"
                else:
                    # Replace with default value
                    current[final_key] = default_value
                    message = f"Successfully reset {key_path} to default: {default_value}"

                # Write back to file
                with open(config_path, "w") as f:
                    f.write(tomlkit.dumps(config))

                progress.update(task, completed=1)

            rich_helper.print_success(message)
            return 0

        except Exception as e:
            logging.error(f"Failed to remove configuration key: {e}")
            rich_helper.print_error(f"Error removing {key_path}: {e}")
            return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(1)
