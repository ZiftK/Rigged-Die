from rich.text import Text


def flatten(lst: list):
    for item in lst:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item


def format_dict(
        dct: dict,
        title: str = "",
        title_style: str = "",
        jumps_before_title: int = 1,
        jumps_after_title: int = 2,
        key_styles: list[str] | None = None,
        default_text="NA",
        ident_level: int = 0,
        jump_count_after_key: int = 0,
) -> str | Text:
    rich_text = Text()

    if not title == "":
        rich_text.append("\n" * jumps_before_title)
        rich_text.append(title, style=title_style)
        jumps = "\n" * jumps_after_title
        rich_text.append(f"{jumps}")

    key_styles = ["default"] if not key_styles else key_styles

    __rich_dict_format(
        dct,
        rich_text,
        key_styles=key_styles,
        default_text=default_text,
        ident_level=ident_level,
        jump_count_after_key=jump_count_after_key
    )

    return rich_text


def format_list(
        lst: list,
        title: str = "",
        title_style: str = "",
        jumps_before_title: int = 1,
        jumps_after_title: int = 2,
        val_styles: list | None = None,
        ident_level: int = 0,
        jumps_after_value: int = 1,
) -> Text:
    rich_text = Text()

    if not title == "":
        rich_text.append("\n" * jumps_before_title)
        rich_text.append(title, style=title_style)
        rich_text.append("\n" * jumps_after_title)

    style_index = 0
    for val in lst:
        rich_text.append("\t" * ident_level)
        rich_text.append(val, style=val_styles[style_index])
        style_index += 1
        style_index %= len(val_styles)

        rich_text.append("\n" * jumps_after_value)

    return rich_text


def __standard_format_dict(dct, indent=0):
    output = ""
    indent_str = " " * 6  # Define el nivel de indentación como 6 espacios

    for key, value in dct.items():
        output += f"{indent_str * indent}{key}:\n"
        if isinstance(value, dict):
            output += __standard_format_dict(value, indent + 1)
        else:
            output += f"{indent_str * (indent + 1)}{value}\n"

    return output


def __rich_dict_format(
        dct: dict,
        rich_text: Text,
        key_styles: list[str] | None = None,
        default_text: str = "NA",
        ident_level: int = 0,
        init_seek: int = 0,
        jump_count_after_key: int = 1,
        style_index=0
):
    max_key_size = max([len(key) for key in dct])

    for key, value in dct.items():

        # get style index
        style_index %= len(key_styles)

        jump = '\n' * jump_count_after_key
        rich_text.append(
            f"{' ' * (init_seek + 1)}{' ' * ident_level}{key}{' ' * (max_key_size - len(key))} ",
            style=key_styles[style_index]
        )
        rich_text.append(f": {jump}")

        if isinstance(value, dict):
            __rich_dict_format(
                value,
                rich_text,
                key_styles=key_styles,
                default_text=default_text,
                ident_level=ident_level + 1,
                init_seek=max_key_size + init_seek,
                style_index=style_index + 1
            )
        else:
            s = default_text if str(value).replace(" ", "") == "" else value
            rich_text.append(f"{' ' * (init_seek + 3 + max_key_size)}{' ' * ident_level}", style="auto")
            rich_text.append(f"{s}")
            rich_text.append("\n")
