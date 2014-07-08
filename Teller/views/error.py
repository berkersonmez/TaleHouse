from Teller.shortcuts.teller_shortcuts import render_with_defaults


def error_info(request, error_message):
    return render_with_defaults(request, 'Teller/error.html', {'error': error_message})