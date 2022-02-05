from datetime import datetime


def year(request):
    """Add variable with current year."""
    now = datetime.now()
    return {'year': now.year}
