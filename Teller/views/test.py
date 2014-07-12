from Teller.shortcuts.teller_shortcuts import render_with_defaults


def test(request):
    return render_with_defaults(request, 'Teller/test.html', {})