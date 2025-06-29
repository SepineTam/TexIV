import argparse
import json

from ..core import TexIV


def main():
    parser = argparse.ArgumentParser(description="TexIV CLI")
    parser.add_argument(
        "content",
        type=str,
        help="Path to the content text file"
    )
    parser.add_argument(
        "keywords",
        type=str,
        help="Path to the keywords file, one keyword per line"
    )
    # TODO: 在此处添加 config 相关的 CLI 选项（例如 --config）
    # TODO: 后续添加批量处理的，如直接传入csv的
    args = parser.parse_args()

    texiv = TexIV()

    with open(args.content, "r", encoding="utf-8") as f:
        content_text = f.read()
    with open(args.keywords, "r", encoding="utf-8") as f:
        keywords_list = [line.strip() for line in f if line.strip()]

    result = texiv.texiv_it(content_text, keywords_list)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
