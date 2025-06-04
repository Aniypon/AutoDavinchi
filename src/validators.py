import re


import re


def check_promoting(self, text) -> tuple[bool, str]:
    """
    Возвращает True, если есть реклама
    """
    text = text.lower()

    for promoting in self.promotings:
        parsed = promoting.split("|")
        searched, reply = parsed[0], parsed[1]
        if searched in text:
            return True, reply

    return False, ""


def check_age(self, age, text) -> tuple[str, bool]:
    """
    Возвращает False, если возраст не подходит
    """

    min_age = self.config["search"]["forms"]["age"]["min_age"]
    max_age = self.config["search"]["forms"]["age"]["max_age"]
    try:
        age_int = int(age)
    except Exception:
        return age, False
    if age_int < min_age or age_int > max_age:
        return age, False

    if self.config["search"]["forms"]["age"]["check_age_in_text"]:
        sub_age = re.findall(r'\s(\d{2}).?', text)
        if len(sub_age) != 0:
            try:
                sub_age = int(sub_age[0])
                if sub_age < min_age or sub_age > max_age:
                    return f"Возраст в тексте - {sub_age}", False
            except Exception:
                return f"Возраст в тексте - {sub_age[0]}", False

    return age, True


def check_about_len(self, text) -> tuple[str, bool]:
    """
    Возвращает False, если длина описания не подходит
    """

    length = len(text)
    if self.config["search"]["forms"]["about_text"]["skip_empty_texts"] and length == 0:
        return "0", False

    return str(length), length >= self.config["search"]["forms"]["about_text"]["minimal_text_size"]


def check_about_banwords(self, text) -> tuple[str, bool]:
    """
    Возвращает False, если найдено бан-слово
    """

    if text == "":
        return "", True

    text = text.lower()
    for banword in self.banwords:
        if banword in text:
            return banword, False

    return "", True
