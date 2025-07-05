import argparse
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
        help="show the program's version number"
    )

    parser.add_argument(
        "-i", "--init",
        action="store_true",
        help="Initialize TexIV configuration"
    )

    # parser.add_argument(
    #     "-U", "--upgrade",
    #     action="store_true",
    #     help="Upgrade TexIV configuration from old one"
    # )

    parser.add_argument(
        "--cat",
        action="store_true",
        help="Show TexIV configuration"
    )

    """
    # Add sub parsers for set and rm commands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands'
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
    """

    args = parser.parse_args()

    if args.init:
        cli.do_init()
    if args.upgrade:
        cli.do_upgrade()
    if args.cat:
        cli.do_cat()
    if args.command == 'set':
        cli.do_set(key_path=args.key_path, value=args.value)
    if args.command == 'rm':
        cli.do_rm(key_path=args.key_path)


class CLI:
    CONFIG_FILE_PATH = Config.CONFIG_FILE_PATH
    IS_EXIST_CONFIG_FILE = Config.is_exist()

    def exit_with_not_exist(self):
        if self.IS_EXIST_CONFIG_FILE:
            pass
        else:
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
        self.exit_with_not_exist()
        print("Not support now")
        sys.exit(0)

    def do_cat(self):
        self.exit_with_not_exist()

        # Show the config file content
        with open(self.CONFIG_FILE_PATH, "r") as f:
            content = f.read()
        print(content)

    def do_set(self, key_path, value):
        self.exit_with_not_exist()
        print("Not support now")
        sys.exit(0)

    @staticmethod
    def do_rm(key_path):
        print("Not support now")
        sys.exit(0)


if __name__ == "__main__":
    main()
