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

from .. import __version__
from ..config import Config
from ..core.utils import yes_or_no


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

    if args.init:
        cli.do_init()
    if args.upgrade:
        cli.do_upgrade()
    if args.cat:
        cli.do_cat()
    if args.command == 'add':
        cli.do_add_key(key=args.key)
    if args.command == 'set':
        cli.do_set(key_path=args.key_path, value=args.value)
    if args.command == 'rm':
        cli.do_rm(key_path=args.key_path)


class CLI:
    CONFIG_FILE_PATH = Config.CONFIG_FILE_PATH
    IS_EXIST_CONFIG_FILE = Config.is_exist()

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
    def do_init():
        print(
            "You are initializing TexIV configuration...\n"
            "You must know that initializing will overwrite your current configuration.")
        flag = yes_or_no("Do you want to continue?")
        if flag:
            Config.cli_init()
        sys.exit(0)

    def do_upgrade(self):
        """
        Upgrade configuration from old versions to new format using template merging.
        Preserves existing settings and adds missing sections with defaults.
        """
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

            # Create backup before upgrade
            shutil.copy2(config_path, backup_path)
            print(f"Configuration backup created at: {backup_path}")

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

            # Create merged config
            merged_config = tomlkit.document()
            deep_merge(merged_config, template)
            deep_merge(merged_config, user_config)

            # Handle API_KEY type conversion (ensure it's always a list)
            for service in ["openai", "ollama"]:
                if service in merged_config["embed"]:
                    api_keys = merged_config["embed"][service]["API_KEY"]
                    if isinstance(api_keys, str):
                        merged_config["embed"][service]["API_KEY"] = [api_keys]
                    elif not isinstance(api_keys, list):
                        merged_config["embed"][service]["API_KEY"] = [
                            str(api_keys)]

            # Write upgraded configuration
            with open(config_path, "w") as f:
                f.write(tomlkit.dumps(merged_config))

            print("Configuration successfully upgraded!")
            print("Backup saved to:", backup_path)
            print("\nUpgrade summary:")
            print("- Configuration structure updated to latest format")
            print("- Missing sections added with default values")
            print("- Existing settings preserved")
            print("- API_KEY values normalized to list format")
            print("- Backup created for safety")

            sys.exit(0)

        except Exception as e:
            logging.error(f"Failed to upgrade configuration: {e}")
            print(f"Error during upgrade: {e}")
            print("Your original configuration remains unchanged.")
            sys.exit(1)

    def do_cat(self):
        self.exit_with_not_exist()

        # Show the config file content
        with open(self.CONFIG_FILE_PATH, "r") as f:
            content = f.read()
        print(content)
        sys.exit(0)

    def do_add_key(self, key):
        self.exit_with_not_exist()
        try:
            Config().add_api_key(key)
            sys.exit(0)
        except Exception as e:
            logging.error(f"Failed to add API key: {e}")
            sys.exit(1)

    def do_set(self, key_path, value):
        """
        Set a configuration value by key path.
        Supports dot notation like: embed.openai.MODEL or texiv.filter.valve
        """
        self.exit_with_not_exist()

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

            # Write back to file
            with open(config_path, "w") as f:
                f.write(tomlkit.dumps(config))

            print(f"Successfully set {key_path} = {parsed_value}")
            sys.exit(0)

        except Exception as e:
            logging.error(f"Failed to set configuration value: {e}")
            print(f"Error setting {key_path}: {e}")
            sys.exit(1)

    def do_rm(self, key_path):
        """
        Remove a configuration key and replace with default value.
        Supports dot notation like: embed.openai.MODEL or texiv.filter.valve
        """
        self.exit_with_not_exist()

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
                    print(f"Key path {key_path} not found in configuration")
                    sys.exit(1)
                current = current[key]

            # Remove the final key
            final_key = keys[-1]
            if final_key not in current:
                print(f"Key {final_key} not found in {'.'.join(keys[:-1])}")
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
            if default_value is None:
                # If no default exists, just remove the key
                del current[final_key]
                print(f"Successfully removed {key_path} (no default value)")
            else:
                # Replace with default value
                current[final_key] = default_value
                print(
                    f"Successfully reset {key_path} to default: {default_value}")

            # Write back to file
            with open(config_path, "w") as f:
                f.write(tomlkit.dumps(config))
            
            sys.exit(0)

        except Exception as e:
            logging.error(f"Failed to remove configuration key: {e}")
            print(f"Error removing {key_path}: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
