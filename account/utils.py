from rest_framework.exceptions import ValidationError

def convert_currency(amount, from_currency, to_currency):
    # Example exchange rates
    exchange_rates = {
        'USD': {'EUR': 0.85, 'ILS': 3.5},
        'EUR': {'USD': 1.18, 'ILS': 4.1},
        'ILS': {'USD': 0.29, 'EUR': 0.24},
    }
    
    if from_currency == to_currency:
        return amount
    
    try:
        conversion_rate = exchange_rates[from_currency][to_currency]
        return amount * conversion_rate
    except KeyError:
        raise ValidationError("Currency conversion not supported.")
