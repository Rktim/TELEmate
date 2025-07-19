"""
F1 Driver Data Utility
Contains driver initials and car numbers only
"""

# F1 Drivers (2018–2025) with Initials and Car Numbers
F1_DRIVERS = {
    'HAM': 44,
    'ALO': 14,
    'LEC': 16,
    'VER': 1,
    'PER': 11,
    'GAS': 10,
    'OCO': 31,
    'RUS': 63,
    'NOR': 4,
    'TSU': 22,
    'ZHO': 24,
    'PIA': 81,
    'SAR': 2,
    'BOT': 77,
    'RIC': 3,
    'HUL': 27,
    'MAG': 20,
    'ALB': 23,
    'STR': 18,
    'KVY': 26,
    'KUB': 88,
    'DEV': 21
}

def get_driver_number(initials):
    """Get driver car number by initials"""
    return F1_DRIVERS.get(initials.upper())

def get_driver_by_number(number):
    """Get driver initials by car number"""
    for initials, num in F1_DRIVERS.items():
        if num == number:
            return initials
    return None

def get_all_driver_initials():
    """Get list of all driver initials"""
    return list(F1_DRIVERS.keys())

def get_all_driver_numbers():
    """Get list of all driver numbers"""
    return list(F1_DRIVERS.values())

def print_driver_list():
    """Print all drivers with their numbers"""
    print("=== F1 Drivers (2018–2025) ===")
    for initials, number in F1_DRIVERS.items():
        print(f"{initials}: #{number}")

if __name__ == "__main__":
    print_driver_list() 