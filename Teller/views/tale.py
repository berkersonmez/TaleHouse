from django.utils.text import slugify
from Teller.forms import TalePartForm, TaleAddForm
from Teller.models import Tale, Profile, TalePart
from Teller.shortcuts.teller_shortcuts import render_with_defaults
from django.shortcuts import redirect


def tale_add_part(request, tale_id=0):
    if not request.user.is_authenticated():
        return redirect('error_info', 'Not registered user')
    profile = Profile.objects.get(user__username=request.user.username)

    if tale_id != 0:
        form = TalePartForm(profile, initial={'tale': tale_id})
    elif request.method == 'POST':
        form = TalePartForm(profile, data=request.POST)
        if form.is_valid():
            tale = form.cleaned_data['tale']
            name = form.cleaned_data['name']
            content = form.cleaned_data['content']
            is_active = form.cleaned_data['is_active']
            poll_end_date = form.cleaned_data['poll_end_date']
            slug = slugify(name)
            if tale is None:
                redirect('error_info', 'Tale not found')
            tale_part = TalePart.objects.create(tale=tale,
                                                name=name,
                                                content=content,
                                                is_active=is_active,
                                                poll_end_date=poll_end_date,
                                                slug=slug)
            if tale_part is None:
                return redirect('error_info', 'Tale part could not be created')
            return redirect('index')
    else:
        form = TalePartForm(profile)

    context = {'tale_add_part_form': form}
    return render_with_defaults(request, 'Teller/tale_add_part.html', context)


def tale_add(request):
    if not request.user.is_authenticated():
        return redirect('error_info', 'Not registered user')
    profile = Profile.objects.get(user__username=request.user.username)
    if request.method == 'POST':
        form = TaleAddForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            language = form.cleaned_data['language']
            is_poll_tale = form.cleaned_data['is_poll_tale']
            slug = slugify(name)
            tale = Tale.objects.create(name=name,
                                       language=language,
                                       is_poll_tale=is_poll_tale,
                                       user=profile,
                                       slug=slug)
            if tale is None:
                return redirect('error_info', 'Tale could not be created')
            return redirect('tale_add_part_idgiven', tale.pk)
    else:
        form = TaleAddForm()
    context = {'tale_add_form': form}
    return render_with_defaults(request, 'Teller/tale_add.html', context)