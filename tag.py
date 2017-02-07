from typing import Tuple, List


class Tag(object):
    # TODO +indent
    def __init__(self, tag_name: str, value: Tuple[str] or List[str], indent_level: int = 0):
        is_acceptable = tag_name.lower() in ["rem", "file", "track", "index", "title", "performer"]
        if not is_acceptable:
            raise ValueError("Сие наименование тега не допустимо")
        if not isinstance(value, tuple) and not isinstance(value, list) or len(value) < 1:
            raise ValueError("Недопустимый список значений тега")
        self.tag_name = tag_name
        self.value = value
        self.__indent_level__ = indent_level

    def __str__(self):
        tag = self.tag_name.lower()
        has_1quotes = tag == "title" or tag == "performer" or tag == "file"
        has_2arg = len(self.value) == 2
        has_2quotes = tag == "comment"

        arg1 = "{1}{0}{1}".format(self.value[0], "\"" if has_1quotes else "")
        if has_2arg and not has_1quotes:
            arg1 = arg1.upper()
        arg2 = "{1}{0}{1}".format(self.value[1], "\"" if has_2quotes else "") if has_2arg else ""
        return "{0} {1} {2}".format(tag.upper(), arg1, arg2)

    def iss(self, name: str):
        result = name.lower().startswith(self.tag_name.lower())
        if self.tag_name.lower() == "rem" and result:
            result = result and name.endswith(self.value[0].lower())
        return result
