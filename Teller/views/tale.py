from django.utils.text import slugify
import pprint
from Teller.forms import TalePartForm, TaleAddForm, TaleLinkAddForm, TaleEditPartForm, TaleLinkEditForm, TaleSearchForm
from Teller.models import Tale, Profile, TalePart, TaleLink, Rating
from Teller.shortcuts.tarjans_cycle_detection import TarjansCycleDetection
from Teller.shortcuts.teller_shortcuts import render_with_defaults
from django.shortcuts import redirect
from django.db.models import Q, Count
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from decimal import *


# TODO: This can be better:
def part_status(key):
    vals = {'VOTE': 0, 'ERROR': 1, 'END': 2, 'READ': 3, 'DATE_CONSTRAINT': 4}
    return vals[key]


def part_status_vals():
    return {'VOTE': 0, 'ERROR': 1, 'END': 2, 'READ': 3, 'DATE_CONSTRAINT': 4}


def add_lists_to_context(context, tale):
    tale_part_list = TalePart.objects.filter(tale=tale)
    tale_link_list = None
    if tale_part_list.count() > 0:
        tale_link_list = TaleLink.objects.filter(tale=tale)
    context.update({'tale_link_list': tale_link_list, 'tale_part_list': tale_part_list})
    return context


def get_last_part(tale, user, page_no):
    page_no = int(page_no)
    if page_no <= 0 and page_no != -1:
        page_no = 1
    i = 0
    try:
        current_part = TalePart.objects.get(tale=tale, is_start=True)
    except TalePart.DoesNotExist:
        return {'message': _('Tale does not have a starting part'), 'status': part_status('ERROR')}
    while page_no == -1 or i < page_no:
        i += 1
        if not current_part.is_active:
            return {'message': _('This tale part is not activated yet'), 'status': part_status('ERROR'), 'page': i}
        links = TaleLink.objects.filter(tale=tale, source=current_part)
        if links.count() == 0:
            return {'status': part_status('END'), 'message': _('Tale part does not have any links'),
                    'part': current_part, 'page': i}
        selected_link = links.filter(profile=user)
        if selected_link.count() == 0:
            return {'part': current_part, 'status': part_status('VOTE'), 'links': links, 'page': i}
        if i == page_no:
            return {'part': current_part, 'status': part_status('READ'), 'links': links,
                    'selected_link': selected_link[0], 'page': i}
        current_part = selected_link[0].destination
    return {'status': part_status('ERROR'), 'message': _('Unknown error')}


def get_last_part_poll(tale, user, page_no):
    page_no = int(page_no)
    if page_no <= 0 and page_no != -1:
        page_no = 1
    i = 0
    try:
        current_part = TalePart.objects.get(tale=tale, is_start=True)
    except TalePart.DoesNotExist:
        return {'message': _('Tale does not have a starting part'), 'status': part_status('ERROR')}
    while page_no == -1 or i < page_no:
        i += 1
        if not current_part.is_active:
            return {'message': _('This tale part is not activated yet'), 'status': part_status('ERROR'), 'page': i}
        links = TaleLink.objects.filter(tale=tale, source=current_part)
        if links.count() == 0:
            return {'status': part_status('END'), 'message': _('Tale part does not have any links'),
                    'part': current_part, 'page': i}
        selected_link = links.filter(profile=user)
        if current_part.poll_end_date > timezone.now() and selected_link.count() == 0:
            return {'part': current_part, 'status': part_status('VOTE'), 'links': links, 'page': i}
        link_votes = links.annotate(num_votes=Count('profile')).values_list('num_votes')
        links_with_votes = zip(links, link_votes)
        if current_part.poll_end_date > timezone.now() and selected_link.count() > 0:
            return {'part': current_part, 'status': part_status('DATE_CONSTRAINT'), 'selected_link': selected_link[0],
                    'links': links_with_votes, 'page': i}
        voted_link = links.annotate(num_votes=Count('profile')).order_by('-num_votes')[0]
        if i == page_no:
            return {'part': current_part, 'status': part_status('READ'), 'links': links_with_votes,
                    'selected_link': voted_link, 'page': i}
        current_part = voted_link.destination
    return {'status': part_status('ERROR'), 'message': _('Unknown error')}


def tale_read(request, tale_slug, page_no=-1):
    if not request.user.is_authenticated():
        return redirect('error_info', _('Not registered user'))
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale = Tale.objects.get(slug=tale_slug)
    except Tale.DoesNotExist:
        return redirect('error_info', _('Tale not found'))
    if tale.user != profile and not tale.is_published:
        return redirect('error_info', _('Tale not found'))
    if tale.is_poll_tale:
        result = get_last_part_poll(tale, profile, page_no)
    else:
        result = get_last_part(tale, profile, page_no)
    context = {'tale': tale, 'profile': profile, 'result': result, 'status_enum': part_status_vals()}
    return render_with_defaults(request, 'Teller/tale_read.html', context)


def tale_vote(request, tale_slug, tale_link_id, tale_part_id, page_no):
    if not request.user.is_authenticated():
        return redirect('error_info', _('Not registered user'))
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale = Tale.objects.get(slug=tale_slug)
    except Tale.DoesNotExist:
        return redirect('error_info', _('Tale not found'))
    try:
        tale_link = TaleLink.objects.get(id=tale_link_id, tale=tale)
    except TaleLink.DoesNotExist:
        return redirect('error_info', _('Tale link not found'))
    try:
        tale_part = TalePart.objects.get(id=tale_part_id, tale=tale)
    except TalePart.DoesNotExist:
        return redirect('error_info', _('Tale part not found'))
    if TaleLink.objects.filter(source=tale_part).filter(profile=profile).count() > 0:
        return redirect('error_info', _('You have already selected a link for this part'))
    if tale.is_poll_tale and tale_part.poll_end_date < timezone.now():
        return redirect('error_info', _('You cannot vote for this link at this time'))
    profile.selected_links.add(tale_link)
    page_no_int = int(page_no) + 1
    return redirect('tale_read', tale_slug, page_no_int)


def tale_reset(request, tale_slug):
    if not request.user.is_authenticated():
        return redirect('error_info', _('Not registered user'))
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale = Tale.objects.get(slug=tale_slug)
    except Tale.DoesNotExist:
        return redirect('error_info', _('Tale not found'))
    voted_links = TaleLink.objects.filter(tale=tale).filter(profile=profile)
    if tale.is_poll_tale:
        return redirect('error_info', _('Poll tale votes cannot be revoked'))
    for link in voted_links:
        link.profile_set.remove(profile)
    return redirect('tale_read', tale.slug, -1)


def tale_add_link(request, tale_slug):
    if not request.user.is_authenticated():
        return redirect('error_info', _('Not registered user'))
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale = Tale.objects.get(user=profile, slug=tale_slug)
    except Tale.DoesNotExist:
        return redirect('error_info', _('Tale not found'))
    if request.method == 'POST':
        form = TaleLinkAddForm(tale, data=request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            source = form.cleaned_data['source']
            destination = form.cleaned_data['destination']
            tale_link = TaleLink.objects.create(source=source,
                                                destination=destination,
                                                action=action,
                                                tale=tale)
            if tale_link is None:
                return redirect('error_info', _('Tale link could not be created'))
            tarjans_cycle_detection = TarjansCycleDetection(tale.id, tale)
            if tarjans_cycle_detection.detect_cycles():
                tale_link.delete()
                return redirect('error_info', _('Links should not create cycles in the tale'))
            return redirect('tale_details', tale.slug)
    else:
        form = TaleLinkAddForm(tale)
    context = {'tale_add_link_form': form,
               'tale': tale}
    context = add_lists_to_context(context, tale)
    return render_with_defaults(request, 'Teller/tale_add_link.html', context)


def tale_edit_link(request, tale_link_id):
    if not request.user.is_authenticated():
        return redirect('error_info', _('Not registered user'))
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale_link = TaleLink.objects.get(id=tale_link_id, tale__user=profile)
    except TaleLink.DoesNotExist:
        return redirect('error_info', _('Tale link not found'))
    tale = tale_link.tale
    if request.method == 'POST':
        form = TaleLinkEditForm(tale, tale_link.action, data=request.POST)
        if form.is_valid():
            tale_link.action = form.cleaned_data['action']
            tale_link.source = form.cleaned_data['source']
            tale_link.destination = form.cleaned_data['destination']
            tale_link.save()
            return redirect('tale_details', tale.slug)
    else:
        form = TaleLinkEditForm(tale, tale_link.action, tale_link)
    context = {'tale_edit_link_form': form, 'tale_link': tale_link}
    context = add_lists_to_context(context, tale)
    return render_with_defaults(request, 'Teller/tale_edit_link.html', context)


def tale_delete_link(request, tale_link_id):
    if not request.user.is_authenticated():
        return redirect('error_info', _('Not registered user'))
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale_link = TaleLink.objects.get(id=tale_link_id, tale__user=profile)
    except TaleLink.DoesNotExist:
        return redirect('error_info', _('Tale link not found'))
    if tale_link.tale.is_poll_tale and Profile.objects.filter(selected_links=tale_link).count() > 0:
        return redirect('error_info', _('Poll tale link is voted and cannot be deleted'))
    tale = tale_link.tale
    tale_link.delete()
    return redirect('tale_details', tale.slug)


def tale_add_part(request, tale_slug=0):
    if not request.user.is_authenticated():
        return redirect('error_info', _('Not registered user'))
    profile = Profile.objects.get(user__id=request.user.id)

    tale = None
    if tale_slug != 0:
        try:
            tale = Tale.objects.get(slug=tale_slug, user=profile)
        except Tale.DoesNotExist:
            return redirect('error_info', _('Tale not found'))
        form = TalePartForm(profile, tale, initial={'tale': tale_slug})
    elif request.method == 'POST':
        form = TalePartForm(profile, data=request.POST)
        if form.is_valid():
            tale = form.cleaned_data['tale']
            name = form.cleaned_data['name']
            content = form.cleaned_data['content']
            is_active = form.cleaned_data['is_active']
            poll_end_date = form.cleaned_data['poll_end_date']
            is_start = TalePart.objects.filter(tale=tale, is_start=True).count() == 0
            if tale is None:
                redirect('error_info', _('Tale not found'))
            tale_part = TalePart.objects.create(tale=tale,
                                                name=name,
                                                content=content,
                                                is_active=is_active,
                                                poll_end_date=poll_end_date,
                                                is_start=is_start)
            if tale_part is None:
                return redirect('error_info', _('Tale part could not be created'))
            return redirect('tale_details', tale.slug)
    else:
        form = TalePartForm(profile)
    context = {'tale_add_part_form': form}
    context = add_lists_to_context(context, tale)
    return render_with_defaults(request, 'Teller/tale_add_part.html', context)


def tale_edit_part(request, tale_part_id):
    if not request.user.is_authenticated():
        return redirect('error_info', _('Not registered user'))
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale_part = TalePart.objects.get(id=tale_part_id, tale__user=profile)
    except TalePart.DoesNotExist:
        return redirect('error_info', _('Tale part not found'))
    tale = tale_part.tale
    if request.method == 'POST':
        form = TaleEditPartForm(profile, tale, tale_part.name, data=request.POST)
        if form.is_valid():
            tale_part.name = form.cleaned_data['name']
            tale_part.content = form.cleaned_data['content']
            tale_part.is_active = form.cleaned_data['is_active']
            tale_part.poll_end_date = form.cleaned_data['poll_end_date']
            tale_part.save()
            return redirect('tale_details', tale.slug)
    else:
        form = TaleEditPartForm(profile, tale, tale_part.name, tale_part)
    context = {'tale_edit_part_form': form, 'tale_part': tale_part}
    context = add_lists_to_context(context, tale)
    return render_with_defaults(request, 'Teller/tale_edit_part.html', context)


def tale_delete_part(request, tale_part_id):
    if not request.user.is_authenticated():
        return redirect('error_info', _('Not registered user'))
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale_part = TalePart.objects.get(id=tale_part_id, tale__user=profile)
    except TalePart.DoesNotExist:
        return redirect('error_info', _('Tale part not found'))
    if tale_part.is_start:
        return redirect('error_info', _('Starting parts should not be deleted'))
    if TaleLink.objects.filter(Q(source=tale_part) | Q(destination=tale_part)).count() > 0:
        return redirect('error_info', _('Links of the tale part should be deleted first'))
    tale = tale_part.tale
    tale_part.delete()
    return redirect('tale_details', tale.slug)


def tale_add(request):
    if not request.user.is_authenticated():
        return redirect('error_info', _('Not registered user'))
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
                return redirect('error_info', _('Tale could not be created'))
            return redirect('tale_add_part_idgiven', tale.slug)
    else:
        form = TaleAddForm()
    context = {'tale_add_form': form}
    return render_with_defaults(request, 'Teller/tale_add.html', context)


def tale_delete(request, tale_id):
    if not request.user.is_authenticated():
        return redirect('error_info', _('Not registered user'))
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale = Tale.objects.get(id=tale_id, user=profile)
    except Tale.DoesNotExist:
        return redirect('error_info', _('Tale not found'))
    TaleLink.objects.filter(tale=tale).delete()
    TalePart.objects.filter(tale=tale).delete()
    tale.delete()
    return redirect('tale_list')


def tale_details(request, tale_slug):
    if not request.user.is_authenticated():
        return redirect('error_info', _('Not registered user'))
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale = Tale.objects.get(user=profile, slug=tale_slug)
    except Tale.DoesNotExist:
        return redirect('error_info', _('Tale not found'))
    tarjan = TarjansCycleDetection(tale.id, tale)
    tarjan.detect_cycles()
    context = {'tale': tale}
    context = add_lists_to_context(context, tale)
    return render_with_defaults(request, 'Teller/tale_details.html', context)


def tale_list(request):
    if not request.user.is_authenticated():
        return redirect('error_info', _('Not registered user'))
    profile = Profile.objects.get(user__id=request.user.id)
    list_of_tales = Tale.objects.filter(user=profile)
    context = {'tale_list': list_of_tales}
    return render_with_defaults(request, 'Teller/tale_list.html', context)


def tale_publish(request, tale_id):
    if not request.user.is_authenticated():
        return redirect('error_info', _('Not registered user'))
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale = Tale.objects.get(user=profile, id=tale_id)
    except Tale.DoesNotExist:
        return redirect('error_info', _('Tale not found'))
    if not tale.is_published:
        tale.is_published = True
        tale.save()
    return redirect('tale_list')


def tale_rate(request, tale_id, rate_amount):
    if not request.user.is_authenticated():
        return redirect('error_info', _('Not registered user'))
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale = Tale.objects.get(id=tale_id, is_published=True)
    except Tale.DoesNotExist:
        return redirect('error_info', _('Tale not found'))
    if tale.user == profile:
        return redirect('error_info', _('You cannot rate your own tale'))
    if Rating.objects.filter(user=profile, tale=tale).count() > 0:
        return redirect('error_info', _('You have already rated this tale'))
    if rate_amount not in ['1', '2', '3', '4', '5']:
        return redirect('error_info', _('Invalid rate amount'))
    rating = Rating.objects.create(user=profile, tale=tale, rating=Decimal(rate_amount))
    if rating is None:
        return redirect('error_info', _('Rating could not be created'))
    tale_ratings = Rating.objects.filter(tale=tale).values_list('rating', flat=True)
    overall_rating = sum(tale_ratings) / Decimal(len(tale_ratings))
    tale.overall_rating = overall_rating
    tale.save()
    return redirect('tale_read_continue', tale.slug)


def tale_search(request):
    if not request.user.is_authenticated():
        return redirect('error_info', _('Not registered user'))
    profile = Profile.objects.get(user__id=request.user.id)
    page_no = 1
    tale_name = ''
    followed_user_tales = False
    tale_type = 'all'
    order_by = 'rating'
    language = 'all'
    if request.method == 'GET':
        if 'page' in request.GET:
            page_no = request.GET.get('page')
        form = TaleSearchForm(request.GET)
        if form.is_valid():
            tale_name = form.cleaned_data['tale_name']
            followed_user_tales = form.cleaned_data['followed_user_tales']
            tale_type = form.cleaned_data['type']
            order_by = form.cleaned_data['order_by']
            language = form.cleaned_data['language']
    else:
        form = TaleSearchForm()
    tales = Tale.objects.filter(name__contains=tale_name, is_published=True)
    if followed_user_tales:
        if profile.followed_users.all().count() == 0:
            return redirect('error_info', _('You do not follow any users'))
        tales = tales.filter(reduce(
            lambda x, y: x & y, [Q(user=followed_user) for followed_user in profile.followed_users.all()]
        ))
    if tale_type == 'normal':
        tales = tales.filter(is_poll_tale=False)
    elif tale_type == 'poll':
        tales = tales.filter(is_poll_tale=True)
    if order_by == 'name':
        tales = tales.order_by('name')
    elif order_by == 'rating':
        tales = tales.order_by('-overall_rating')
    elif order_by == 'date':
        tales = tales.order_by('created_at')
    if language != 'all':
        tales = tales.filter(language__code=language)
    tale_paginator = Paginator(tales, 25)
    try:
        tales_in_page = tale_paginator.page(page_no)
    except PageNotAnInteger:
        tales_in_page = tale_paginator.page(1)
    except EmptyPage:
        tales_in_page = tale_paginator.page(tale_paginator.num_pages)
    context = {'tale_search_form': form,
               'tales_in_page': tales_in_page,
               'page_no': page_no}
    return render_with_defaults(request, 'Teller/tale_search.html', context)