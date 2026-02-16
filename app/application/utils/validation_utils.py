from __future__ import annotations
import re


_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def is_valid_email(value: str) -> bool:
    if not value:
        return False
    return _EMAIL_RE.match(value) is not None


def only_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def is_valid_cpf_digits(cpf_digits: str) -> bool:
    """
    Validates CPF
    """
    cpf = only_digits(cpf_digits)
    if len(cpf) != 11:
        return False
    if cpf == cpf[0] * 11:
        return False

    def calc_digit(base: str, factor: int) -> str:
        total = 0
        for ch in base:
            total += int(ch) * factor
            factor -= 1
        mod = total % 11
        return "0" if mod < 2 else str(11 - mod)

    d1 = calc_digit(cpf[:9], 10)
    d2 = calc_digit(cpf[:9] + d1, 11)
    return cpf[-2:] == d1 + d2
