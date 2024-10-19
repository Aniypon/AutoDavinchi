import re


def check_promoting(self, text) -> (bool, str):
    """
    Бекаем True если есть реклама
    """
    text = text.lower()

    for promoting in self.promotings:
        parsed = promoting.split("|")
        searched, reply = parsed[0], parsed[1]
        if searched in text:
            return True, reply

    return False, ""


def check_age(self, age, text) -> (str, bool):
    """
    Бекаем False если не подходит
    """

    min_age = self.config["forms"]["age"]["min_age"]
    max_age = self.config["forms"]["age"]["max_age"]

    if int(age) < min_age or int(age) > max_age:
        return age, False

    if self.config["forms"]["age"]["check_age_in_text"]:
        sub_age = re.findall(r'\d{2}', text)  # Ну тут сам головой думай с регуляркой
        if len(sub_age) != 0:
            sub_age = int(sub_age[0])
            if sub_age < min_age or sub_age > max_age:
                return f"Возраст в тексте - {sub_age}", False

    return age, True


def check_about_len(self, text) -> (str, bool):
    """
    Бекаем False если не подходит
    """

    length = len(text)
    if self.config["forms"]["about_text"]["skip_empty_texts"] and length == 0:
        return "0", False

    return str(length), length >= self.config["forms"]["about_text"]["minimal_text_size"]


def check_about_banwords(self, text) -> (str, bool):
    """
    Бекаем False если не подходит
    """

    if text == "":
        return

    text = text.lower()
    for banword in self.banwords:
        if banword in text:
            return banword, False

    return "", True
