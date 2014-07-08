from Teller.shortcuts.teller_shortcuts import render_with_defaults


def index(request):
    return render_with_defaults(request, 'Teller/index.html', {})