from django.utils.text import slugify
from Teller.forms import TalePartForm, TaleAddForm
from Teller.models import Tale, Profile, TalePart, TaleLink
from Teller.shortcuts.teller_shortcuts import render_with_defaults
from django.shortcuts import redirect
from django.db.models import Q


def tale_add_part(request, tale_slug=0):
    if not request.user.is_authenticated():
        return redirect('error_info', 'Not registered user')
    profile = Profile.objects.get(user__id=request.user.id)

    if tale_slug != 0:
        form = TalePartForm(profile, initial={'tale': tale_slug})
    elif request.method == 'POST':
        form = TalePartForm(profile, data=request.POST)
        if form.is_valid():
            tale = form.cleaned_data['tale']
            name = form.cleaned_data['name']
            content = form.cleaned_data['content']
            is_active = form.cleaned_data['is_active']
            poll_end_date = form.cleaned_data['poll_end_date']
            slug = slugify(name)
            is_start = TalePart.objects.filter(tale=tale, is_start=True).count() == 0
            if tale is None:
                redirect('error_info', 'Tale not found')
            tale_part = TalePart.objects.create(tale=tale,
                                                name=name,
                                                content=content,
                                                is_active=is_active,
                                                poll_end_date=poll_end_date,
                                                slug=slug,
                                                is_start=is_start)
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
    profile = Profile.objects.get(user__id=request.user.id)
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
            return redirect('tale_add_part_idgiven', tale.slug)
    else:
        form = TaleAddForm()
    context = {'tale_add_form': form}
    return render_with_defaults(request, 'Teller/tale_add.html', context)


def tale_details(request, tale_slug):
    if not request.user.is_authenticated():
        return redirect('error_info', 'Not registered user')
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale = Tale.objects.get(user=profile, slug=tale_slug)
    except Tale.DoesNotExist:
        return redirect('error_info', 'Tale not found')
    tale_part_list = TalePart.objects.filter(tale=tale)
    tale_link_list = None
    if tale_part_list.count() > 0:
        tale_link_list = TaleLink.objects.filter(
            reduce(lambda x, y: x | y, [Q(source=part) | Q(destination=part) for part in tale_part_list])
        )
    context = {'tale': tale, 'tale_part_list': tale_part_list, 'tale_link_list': tale_link_list}
    return render_with_defaults(request, 'Teller/tale_details.html', context)


def tale_list(request):
    if not request.user.is_authenticated():
        return redirect('error_info', 'Not registered user')
    profile = Profile.objects.get(user__id=request.user.id)
    list_of_tales = Tale.objects.filter(user=profile)
    context = {'tale_list': list_of_tales}
    return render_with_defaults(request, 'Teller/tale_list.html', context)