from datetime import date, datetime

def date_difference(my_date):
    """Calculates the time (in full years and extra days) between a date and today."""
    if my_date == "" or my_date == None:
        return 0, 0
    if not isinstance(my_date, date):
        my_date = datetime.strptime(my_date, "%Y-%m-%d").date()
    today = date.today()

    years = today.year - my_date.year
    # Substract 1 from total years if a full year has not passed from "my_date" this year
    if (today.month, today.day) < (my_date.month, my_date.day):
        years -= 1

    # Calculate the date when the latest full year was reached
    anniversary = date(my_date.year + years, my_date.month, my_date.day)

    # Calculate the leftover days after the full years
    extra_days = (today - anniversary).days

    return years, extra_days