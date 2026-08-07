"""Construcción del dataset ISO global empaquetado con la aplicación."""

import pycountry
from babel import Locale
from babel.numbers import get_currency_precision

from app.modules.referencias.domain import Moneda, Pais

_SIMBOLOS_COMUNES = {
    "ARS": "$",
    "BRL": "R$",
    "CLP": "$",
    "CNY": "¥",
    "COP": "$",
    "EUR": "€",
    "GBP": "£",
    "INR": "₹",
    "JPY": "¥",
    "KRW": "₩",
    "MXN": "$",
    "PEN": "S/",
    "USD": "$",
}


def catalogos_iso() -> tuple[tuple[Pais, ...], tuple[Moneda, ...]]:
    """Devuelve países ISO 3166-1 y monedas ISO 4217 con nombres legibles."""
    locale = Locale("es")
    paises = tuple(
        Pais(
            codigo=str(item.alpha_2),
            nombre=str(locale.territories.get(item.alpha_2, item.name)),
        )
        for item in pycountry.countries
    )
    monedas = tuple(
        Moneda(
            codigo=str(item.alpha_3),
            nombre=str(locale.currencies.get(item.alpha_3, item.name)),
            simbolo=_SIMBOLOS_COMUNES.get(
                str(item.alpha_3),
                str(locale.currency_symbols.get(item.alpha_3, item.alpha_3)),
            ),
            decimales=get_currency_precision(str(item.alpha_3)),
        )
        for item in pycountry.currencies
        if len(str(item.alpha_3)) == 3
    )
    return paises, monedas
