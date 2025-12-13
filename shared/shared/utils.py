import re
from django.core.exceptions import ValidationError

def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False
    # cálculo dos dígitos verificadores
    def calc_digito(cpf_parte):
        soma = sum(int(cpf_parte[i]) * (len(cpf_parte) + 1 - i) for i in range(len(cpf_parte)))
        digito = (soma * 10) % 11
        return digito if digito < 10 else 0
    return (calc_digito(cpf[:9]) == int(cpf[9]) and
     calc_digito(cpf[:10]) == int(cpf[10]))

def validate_cpf(value):
    if not validar_cpf(value):
        raise ValidationError("CPF inválido")

def formatar_telefone(telefone: str) -> str:
    numeros = re.sub(r'\D', '', telefone)
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    return telefone