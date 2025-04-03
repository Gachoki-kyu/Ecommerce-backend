import random

def calculate_return(investment):
    if investment.plan == "fixed":
        return investment.amount * 0.10
    elif investment.plan == "market-based":
        fluctuation = 0.05 + random.random() * 0.10
        return investment.amount * fluctuation
    return 0