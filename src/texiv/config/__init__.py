#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : __init__.py

import logging
import os
import shutil
import sys
from typing import List

import tomlkit
import tomllib

from ..core.utils import yes_or_no


class Config:
    CONFIG_FILE_PATH = os.path.expanduser("~/.texiv/config.toml")
    DEFAULT_CONFIG_FILE_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "example.config.toml")
    )
    BASE_DIR = os.path.dirname(CONFIG_FILE_PATH)

    def __init__(self):
        try:
            self.cfg = self._load_config()
        except FileNotFoundError as e:
            logging.warning(f"Config file not found: {e}")
            if not os.path.exists(self.CONFIG_FILE_PATH):
                os.makedirs(os.path.dirname(self.CONFIG_FILE_PATH),
                            exist_ok=True)
                shutil.copy(self.DEFAULT_CONFIG_FILE_PATH,
                            self.CONFIG_FILE_PATH)

                is_default = input(
                    "Whether to use the default configuration "
                    "(depending on local ollama, using the bge-m3:latest model): "
                ).lower() == 'y'
                if not is_default:
                    self._init_set_config()
        finally:
            self.cfg = self._load_config()
        self._embed_type = self.cfg.get("embed").get(
            "EMBED_TYPE", "ollama"
        ).lower()

    def add_api_key(self, key: str) -> None:
        key_path = f"embed.{self._embed_type}.API_KEY"
        now_key_list: List[str] = self.cfg.get(
            "embed"
        ).get(self._embed_type).get("API_KEY")
        self.set_config(key_path, now_key_list.append(key))
        return None

    def _load_config(self):
        with open(self.CONFIG_FILE_PATH, "rb") as f:
            cfg = tomllib.load(f)
        return cfg

    def set_config(self, key_path: str, value):
        """
        Set config with key-value

        Args:
            key_path (str): index of the key
            value: the value of the key

        Usage:
            >>> Config().set_config("embed.openai.MODEL", "text-embedding-3-large")
        """
        self.cfg = self._load_config()
        keys = key_path.split(".")
        current = self.cfg

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

        self._write_config_to_disk()

    def _write_config_to_disk(self):
        """
        Write the config to disk
        """
        with open(self.CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            parsed = tomlkit.parse(tomlkit.dumps(self.cfg))
            f.write(tomlkit.dumps(parsed))

    def _init_set_config(self):
        while True:
            EMBED_TYPE = input(
                "Please choose your embed type (ollama/openai): \n").lower()
            if EMBED_TYPE in ['ollama', 'openai']:
                break
            else:
                print("Invalid input. Please enter either 'ollama' or 'openai'.")
        self.set_config("embed.EMBED_TYPE", EMBED_TYPE)

        if EMBED_TYPE == "ollama":
            self._init_set_ollama_config()
        elif EMBED_TYPE == "openai":
            self._init_set_openai_config()

    def _set_config_with_input(self, key_path: str, key_prompt: str) -> None:
        ask_value_msg = f"Please enter your model provider {key_prompt}: \n"
        value = input(ask_value_msg)
        while True:
            flag = input(f"Please make sure your input is True:\n"
                         f"\t{key_prompt}: {value}\n"
                         f"Proceed (Y/n)? ")
            if flag.lower() in ["y", "yes"]:
                self.set_config(key_path=key_path, value=value)
                logging.info(f"Setting {key_path}: {value}")
                return None
            elif flag.lower() in ["n", "no"]:
                print("Please re-enter your input.")
                value = input(ask_value_msg)
            else:
                print("Invalid input. Please enter either 'y' or 'n'.")

    def _init_embed_fields(self, provider: str, fields: List[str]):
        for field in fields:
            key_path = f"embed.{provider}.{field}"
            key_prompt = field
            self._set_config_with_input(key_path=key_path,
                                        key_prompt=key_prompt)

    def _init_set_ollama_config(self):
        while True:
            MODEL = input("Please enter your model name: \n")
            if MODEL:
                break
            else:
                print("Invalid input. Please enter a model name.")
        self.set_config("embed.ollama.MODEL", MODEL)

    def _init_set_openai_config(self):
        provider: str = "openai"
        fields: List[str] = ["MODEL", "BASE_URL", "API_KEY"]
        self._init_embed_fields(provider=provider, fields=fields)

    @staticmethod
    def cp_config_file():
        os.makedirs(Config.BASE_DIR, exist_ok=True)
        shutil.copy(Config.DEFAULT_CONFIG_FILE_PATH,
                    Config.CONFIG_FILE_PATH)
        print("Config file created at:", Config.CONFIG_FILE_PATH)

    @staticmethod
    def cli_init():
        # Check whether exist the config file of Config.CONFIG_FILE_PATH
        if os.path.exists(Config.CONFIG_FILE_PATH):
            print("There is existing config file")
            flag = yes_or_no("Whether overwrite the existing config file?")
            if not flag:
                sys.exit(0)
            # Remove the config file
            os.remove(Config.CONFIG_FILE_PATH)
        # Now there is not existing config file
        Config.cp_config_file()

    @staticmethod
    def is_exist() -> bool:
        return os.path.exists(Config.CONFIG_FILE_PATH)


if __name__ == "__main__":
    cfg = Config()
