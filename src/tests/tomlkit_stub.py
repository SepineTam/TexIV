import tomllib

def parse(s):
    return tomllib.loads(s)

def dumps(data):
    lines = []
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"[{key}]")
            for k2, v2 in value.items():
                if isinstance(v2, str):
                    lines.append(f"{k2} = \"{v2}\"")
                else:
                    lines.append(f"{k2} = {v2}")
            lines.append("")
        else:
            if isinstance(value, str):
                lines.append(f"{key} = \"{value}\"")
            else:
                lines.append(f"{key} = {value}")
    return "\n".join(lines)
