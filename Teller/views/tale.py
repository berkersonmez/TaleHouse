from Teller.forms import TalePartForm
from Teller.shortcuts.teller_shortcuts import render_with_defaults


def tale_add_part(request):
    form = TalePartForm()
    context = {'tale_add_part_form': form}
    return render_with_defaults(request, 'Teller/tale_add_part.html', context)