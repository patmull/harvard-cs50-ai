from datetime import datetime


def convert_month_shortcuts_to_integers(month_shortcut):
    print(month_shortcut)
    try:
        month_number = datetime.strptime(month_shortcut, '%b').month
    except ValueError as ve:
        if "unconverted data remains" in str(ve):
            month_number = datetime.strptime(month_shortcut, '%B').month
    return month_number

