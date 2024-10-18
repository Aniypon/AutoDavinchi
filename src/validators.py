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
            return True, promoting

    return False, ""


def check_age(self, age, text) -> (str, bool):
    """
    Бекаем True если не подходит
    """
    if self.config["forms"]["age"]["min_age"] > int(age) > self.config["forms"]["age"]["min_age"]:
        return age, True

    if self.config["forms"]["age"]["check_age_in_text"]:
        sub_age = re.findall(r'\d{2}', text)  # Ну тут сам головой думай с регуляркой
        if len(sub_age) > 0 and self.config["forms"]["age"]["min_age"] > int(sub_age[0]) > self.config["forms"]["age"]["min_age"]:
            return f"Возраст в тесте - {sub_age}", True

    return 0, False


def check_about_len(self, text) -> (str, bool):
    """
    Бекаем True если не подходит
    """
    length = len(text)
    print(length)
    print(self.config["forms"]["about_text"]["skip_empty_texts"])
    print(self.config["forms"]["about_text"]["minimal_text_size"])
    if self.config["forms"]["about_text"]["skip_empty_texts"]:
        return str(length), length == 0

    return str(length), length < self.config["forms"]["about_text"]["minimal_text_size"]


def check_about_banwords(self, text) -> (str, bool):
    """
    Бекаем True если не подходит
    """

    if text == "":
        return

    text = text.lower()
    for banword in self.banwords:
        if banword in text:
            return banword, True

    return "", False
