import datetime
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from lxml import etree
import pprint
from Teller.forms import TalePartForm, TaleAddForm, TaleLinkAddForm, TaleEditPartForm, TaleLinkEditForm, TaleSearchForm, \
    TaleVariableAddForm, TaleVariableEditForm, TalePreconditionAddForm, TaleConsequenceAddForm, TaleCommentAddForm
from Teller.models import Tale, Profile, TalePart, TaleLink, Rating, TaleVariable, TaleLinkPrecondition, \
    TaleLinkConsequence, TalePartComment
from Teller.shortcuts.tarjans_cycle_detection import TarjansCycleDetection
from Teller.shortcuts.teller_content_parser import TellerContentParser
from Teller.shortcuts.teller_shortcuts import render_with_defaults, redirect_with_next
from django.shortcuts import redirect
from django.db.models import Q, Count
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from decimal import *
from django.http import HttpResponse, Http404, HttpResponseRedirect
import json
from django.db import IntegrityError, transaction
from django.conf import settings


# TODO: This can be better:
def part_status(key):
    vals = {'VOTE': 0, 'ERROR': 1, 'END': 2, 'READ': 3, 'DATE_CONSTRAINT': 4}
    return vals[key]


def part_status_vals():
    return {'VOTE': 0, 'ERROR': 1, 'END': 2, 'READ': 3, 'DATE_CONSTRAINT': 4}


def add_lists_to_context(context, tale):
    tale_part_list = TalePart.objects.filter(tale=tale)
    tale_variable_list = TaleVariable.objects.filter(tale=tale)
    tale_link_list = None
    if tale_part_list.count() > 0:
        tale_link_list = TaleLink.objects.filter(tale=tale)
    context.update({'tale_link_list': tale_link_list, 'tale_part_list': tale_part_list,
                    'tale_variable_list': tale_variable_list})
    return context


def get_last_part(tale, user, page_no):
    page_no = int(page_no)
    if page_no <= 0 and page_no != -1:
        page_no = 1
    i = 0
    try:
        current_part = TalePart.objects.get(tale=tale, is_start=True)
        variables = TaleVariable.objects.filter(tale=tale)
        for variable in variables:
            variable.init_value()
    except TalePart.DoesNotExist:
        return {'message': _('Tale does not have a starting part'), 'status': part_status('ERROR')}
    while page_no == -1 or i < page_no:
        i += 1
        if not current_part.is_active:
            return {'message': _('This tale part is not activated yet'), 'part': current_part, 'status': part_status('ERROR'), 'page': i}
        links = TaleLink.objects.filter(tale=tale, source=current_part)

        links = [x for x in links if x.check_conditions(variables)]
        if len(links) == 0:
            return {'status': part_status('END'), 'message': _('Tale part does not have any links'),
                    'part': current_part, 'page': i, 'variables': variables}
        if user is None:
            return {'part': current_part, 'status': part_status('VOTE'),
                    'links': links, 'page': i, 'variables': variables}
        selected_link = [x for x in links if user.selected_links.filter(id=x.id)]
        if len(selected_link) == 0:
            return {'part': current_part, 'status': part_status('VOTE'),
                    'links': links, 'page': i, 'variables': variables}
        if i == page_no:
            return {'part': current_part, 'status': part_status('READ'),
                    'links': links,
                    'selected_link': selected_link[0], 'page': i, 'variables': variables}
        selected_link[0].apply_consequences(variables)
        current_part = selected_link[0].destination
    return {'status': part_status('ERROR'), 'message': _('Unknown error')}


def get_last_part_poll(tale, user, page_no):
    page_no = int(page_no)
    if page_no <= 0 and page_no != -1:
        page_no = 1
    i = 0
    try:
        current_part = TalePart.objects.get(tale=tale, is_start=True)
        variables = TaleVariable.objects.filter(tale=tale)
        for variable in variables:
            variable.init_value()
    except TalePart.DoesNotExist:
        return {'message': _('Tale does not have a starting part'), 'status': part_status('ERROR')}
    while page_no == -1 or i < page_no:
        i += 1
        if not current_part.is_active:
            return {'message': _('This tale part is not activated yet'), 'part': current_part, 'status': part_status('ERROR'), 'page': i}
        links = TaleLink.objects.filter(tale=tale, source=current_part)
        if links.count() == 0:
            return {'status': part_status('END'), 'message': _('Tale part does not have any links'),
                    'part': current_part, 'page': i, 'variables': variables}
        selected_link = links.filter(profile=user)
        if current_part.poll_end_date > timezone.now() and selected_link.count() == 0:
            return {'part': current_part, 'status': part_status('VOTE'), 'links': links, 'page': i,
                    'variables': variables}
        link_votes = links.annotate(num_votes=Count('profile')).values_list('num_votes')
        links_with_votes = zip(links, link_votes)
        if current_part.poll_end_date > timezone.now() and selected_link.count() > 0:
            return {'part': current_part, 'status': part_status('DATE_CONSTRAINT'), 'selected_link': selected_link[0],
                    'links': links_with_votes, 'page': i, 'variables': variables}
        voted_link = links.annotate(num_votes=Count('profile')).order_by('-num_votes')[0]
        if i == page_no:
            return {'part': current_part, 'status': part_status('READ'), 'links': links_with_votes,
                    'selected_link': voted_link, 'page': i, 'variables': variables}
        voted_link.apply_consequences(variables)
        current_part = voted_link.destination
    return {'status': part_status('ERROR'), 'message': _('Unknown error')}


def edit_preconditions_and_consequences(json_data, tale_link):
    tale = tale_link.tale
    precons = json_data['precons']
    precons_deleted = json_data['preconsDeleted']
    conseqs = json_data['conseqs']
    conseqs_deleted = json_data['conseqsDeleted']
    for key, value in precons.items():
        precon_form = TalePreconditionAddForm(tale, data=value)
        if not precon_form.is_valid():
            raise ValueError(precon_form.errors.keys()[0] + ": " + precon_form.errors.values()[0][0])
        tale_variable = precon_form.cleaned_data['tale_variable']
        condition = precon_form.cleaned_data['condition']
        value = precon_form.cleaned_data['value']
        if TaleLinkPrecondition.objects.filter(tale_link=tale_link, tale_variable=tale_variable).count() > 0:
            precon = TaleLinkPrecondition.objects.get(tale_link=tale_link, tale_variable=tale_variable)
            precon.condition = condition
            precon.value = value
            precon.save()
        else:
            TaleLinkPrecondition.objects.create(tale_link=tale_link,
                                                tale_variable=tale_variable,
                                                condition=condition,
                                                value=value)
    for key, value in precons_deleted.items():
        if value and TaleLinkPrecondition.objects.filter(tale_link=tale_link, tale_variable__id=key).count() > 0:
            precon = TaleLinkPrecondition.objects.get(tale_link=tale_link, tale_variable__id=key)
            precon.delete()
    for key, value in conseqs.items():
        conseq_form = TaleConsequenceAddForm(tale, data=value)
        if not conseq_form.is_valid():
            raise ValueError(conseq_form.errors.keys()[0] + ": " + conseq_form.errors.values()[0][0])
        tale_variable = conseq_form.cleaned_data['tale_variable']
        consequence = conseq_form.cleaned_data['consequence']
        value = conseq_form.cleaned_data['value']
        if TaleLinkConsequence.objects.filter(tale_link=tale_link, tale_variable=tale_variable).count() > 0:
            conseq = TaleLinkConsequence.objects.get(tale_link=tale_link, tale_variable=tale_variable)
            conseq.consequence = consequence
            conseq.value = value
            conseq.save()
        else:
            TaleLinkConsequence.objects.create(tale_link=tale_link,
                                               tale_variable=tale_variable,
                                               consequence=consequence,
                                               value=value)
    for key, value in conseqs_deleted.items():
        if value and TaleLinkConsequence.objects.filter(tale_link=tale_link, tale_variable__id=key).count() > 0:
            conseq = TaleLinkConsequence.objects.get(tale_link=tale_link, tale_variable__id=key)
            conseq.delete()


def tale_read(request, tale_slug, page_no=-1):
    if request.user.is_authenticated():
        profile = Profile.objects.get(user__id=request.user.id)
    else:
        profile = None
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

    if 'part' in result and 'variables' in result:
        try:
            content_parser = TellerContentParser()
            content_parser.prepare_conditional_content(result['part'], profile, result['variables'])
        except etree.XMLSyntaxError:
            return redirect('error_info', _('An error occurred'))
        except etree.ParseError:
            return redirect('error_info', _('An error occurred'))
        except etree.Error:
            return redirect('error_info', _('An error occurred'))

    context = {'tale': tale, 'profile': profile, 'result': result, 'status_enum': part_status_vals(),
               'fb_app_id': settings.SOCIAL_AUTH_FACEBOOK_KEY}
    return render_with_defaults(request, 'Teller/tale_read.html', context)


def tale_vote(request, tale_slug, tale_link_id, tale_part_id, page_no):
    if not request.user.is_authenticated():
        return redirect_with_next('user_add', request.path)
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
    if not tale_link.source.id == tale_part.id:
        return redirect('error_info', _('This link does not belong to the given part'))
    if not tale.is_poll_tale and not tale_part.is_start and TaleLink.objects.filter(destination=tale_part).filter(profile=profile).count() == 0:
        return redirect('error_info', _('You cannot take that action'))
    if TaleLink.objects.filter(source=tale_part).filter(profile=profile).count() > 0:
        return redirect('error_info', _('You have already selected a link for this part'))
    if tale.is_poll_tale and tale_part.poll_end_date < timezone.now():
        return redirect('error_info', _('You cannot vote for this link at this time'))
    profile.selected_links.add(tale_link)
    page_no_int = int(page_no) + 1
    return redirect('tale_read', tale_slug, page_no_int)


def tale_reset(request, tale_slug):
    if not request.user.is_authenticated():
        return redirect_with_next('user_add', request.path)
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
        return HttpResponse(_('User is not authenticated'))
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale = Tale.objects.get(user=profile, slug=tale_slug)
    except Tale.DoesNotExist:
        return redirect('error_info', _('Tale not found'))
    if request.is_ajax():
        json_data = json.loads(request.POST['json_data'])
        try:
            with transaction.atomic():
                post_vals = json_data['postVals']
                link_form = TaleLinkAddForm(tale, data=post_vals)
                if not link_form.is_valid():
                    raise ValueError(link_form.errors.keys()[0] + ": " + link_form.errors.values()[0][0])
                name = link_form.cleaned_data['name']
                action = link_form.cleaned_data['action']
                source = link_form.cleaned_data['source']
                destination = link_form.cleaned_data['destination']
                if TaleLink.objects.filter(source=source).count() >= settings.TELLER_MAX_LINKS_PER_PART:
                    raise ValueError(_('Parts can contain maximum of %(max_links_per_part)s links') %
                                     {'max_links_per_part': settings.TELLER_MAX_LINKS_PER_PART})
                tale_link = TaleLink.objects.create(source=source,
                                                    destination=destination,
                                                    name=name,
                                                    action=action,
                                                    tale=tale)
                if tale_link is None:
                    raise ValueError(_('Tale link could not be created'))
                tarjans_cycle_detection = TarjansCycleDetection(tale.id, tale)
                if tarjans_cycle_detection.detect_cycles():
                    raise ValueError(_('Links should not create cycles in the tale'))
                edit_preconditions_and_consequences(json_data, tale_link)
        except IntegrityError:
            return HttpResponse(_('An error is occured'))
        except KeyError:
            return HttpResponse(_('Incorrect JSON'))
        except ValueError as e:
            return HttpResponse(_(e.message))
        return HttpResponse('OK')
    else:
        form = TaleLinkAddForm(tale)
        preconditions_form = TalePreconditionAddForm(tale)
        consequences_form = TaleConsequenceAddForm(tale)
        context = {'tale_add_link_form': form,
                   'tale_add_preconditions_form': preconditions_form,
                   'tale_add_consequences_form': consequences_form,
                   'tale': tale}
        context = add_lists_to_context(context, tale)
        return render_with_defaults(request, 'Teller/tale_add_link.html', context)


def tale_edit_link(request, tale_link_id):
    if not request.user.is_authenticated():
        return HttpResponse(_('User is not authenticated'))
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale_link = TaleLink.objects.get(id=tale_link_id, tale__user=profile)
    except TaleLink.DoesNotExist:
        return redirect('error_info', _('Tale link not found'))
    tale = tale_link.tale
    if request.is_ajax():
        json_data = json.loads(request.POST['json_data'])
        try:
            with transaction.atomic():
                post_vals = json_data['postVals']
                link_form = TaleLinkEditForm(tale, tale_link.name, data=post_vals)
                if not link_form.is_valid():
                    raise ValueError(link_form.errors.keys()[0] + ": " + link_form.errors.values()[0][0])
                action = link_form.cleaned_data['action']
                name = link_form.cleaned_data['name']
                source = link_form.cleaned_data['source']
                destination = link_form.cleaned_data['destination']
                tale_link.action = action
                tale_link.name = name
                tale_link.source = source
                tale_link.destination = destination
                tale_link.save()
                tarjans_cycle_detection = TarjansCycleDetection(tale.id, tale)
                if tarjans_cycle_detection.detect_cycles():
                    raise ValueError(_('Links should not create cycles in the tale'))
                edit_preconditions_and_consequences(json_data, tale_link)
        except IntegrityError:
            return HttpResponse(_('An error is occured'))
        except KeyError:
            return HttpResponse(_('Incorrect JSON'))
        except ValueError as e:
            return HttpResponse(_(e.message))
        return HttpResponse('OK')
    else:
        form = TaleLinkEditForm(tale, tale_link.name, tale_link)
        precons = TaleLinkPrecondition.objects.filter(tale_link=tale_link)
        conseqs = TaleLinkConsequence.objects.filter(tale_link=tale_link)
        preconditions_form = TalePreconditionAddForm(tale)
        consequences_form = TaleConsequenceAddForm(tale)
        context = {'tale_edit_link_form': form,
                   'tale_link': tale_link,
                   'tale_link_preconditions': precons,
                   'tale_link_consequences': conseqs,
                   'tale_add_preconditions_form': preconditions_form,
                   'tale_add_consequences_form': consequences_form,
                   'tale': tale}
        context = add_lists_to_context(context, tale)
        return render_with_defaults(request, 'Teller/tale_edit_link.html', context)


def tale_delete_link(request, tale_link_id):
    if not request.user.is_authenticated():
        return redirect_with_next('user_add', request.path)
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
        return redirect_with_next('user_add', request.path)
    profile = Profile.objects.get(user__id=request.user.id)

    tale = None
    if tale_slug == 0:
        return redirect('error_info', _('Tale not found'))
    try:
        tale = Tale.objects.get(slug=tale_slug, user=profile)
    except Tale.DoesNotExist:
        return redirect('error_info', _('Tale not found'))
    if request.method == 'POST':
        form = TalePartForm(profile, tale, initial={'tale': tale_slug}, data=request.POST)
        if form.is_valid():
            tale = form.cleaned_data['tale']
            name = form.cleaned_data['name']
            content = form.cleaned_data['content']
            content_parser = TellerContentParser()
            content = content_parser.clean_html(content)
            is_active = form.cleaned_data['is_active']
            poll_end_date = form.cleaned_data['poll_end_date']
            is_start = TalePart.objects.filter(tale=tale, is_start=True).count() == 0
            if tale is None:
                return redirect('error_info', _('Tale not found'))
            if TalePart.objects.filter(tale=tale).count() >= settings.TELLER_MAX_PARTS_PER_TALE:
                return redirect('error_info', _('Tales can contain maximum of %(max_parts_per_tale)s parts') %
                                {'max_parts_per_tale': settings.TELLER_MAX_PARTS_PER_TALE})
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
        form = TalePartForm(profile, tale, initial={'tale': tale_slug})
    context = {'tale_add_part_form': form, 'tale': tale}
    context = add_lists_to_context(context, tale)
    return render_with_defaults(request, 'Teller/tale_add_part.html', context)


def tale_edit_part(request, tale_part_id):
    if not request.user.is_authenticated():
        return redirect_with_next('user_add', request.path)
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
            content_parser = TellerContentParser()
            tale_part.content = content_parser.clean_html(tale_part.content)
            tale_part.is_active = form.cleaned_data['is_active']
            tale_part.poll_end_date = form.cleaned_data['poll_end_date']
            tale_part.save()
            return redirect('tale_details', tale.slug)
    else:
        form = TaleEditPartForm(profile, tale, tale_part.name, tale_part)
    context = {'tale_edit_part_form': form, 'tale_part': tale_part, 'tale': tale}
    context = add_lists_to_context(context, tale)
    return render_with_defaults(request, 'Teller/tale_edit_part.html', context)


def tale_delete_part(request, tale_part_id):
    if not request.user.is_authenticated():
        return redirect_with_next('user_add', request.path)
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


def tale_activate_part(request, tale_part_id):
    if not request.user.is_authenticated():
        return redirect_with_next('user_add', request.path)
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale_part = TalePart.objects.get(id=tale_part_id, tale__user=profile)
    except TalePart.DoesNotExist:
        return redirect('error_info', _('Tale part not found'))
    tale_part.is_active = not tale_part.is_active
    tale_part.save()
    return redirect('tale_details', tale_part.tale.slug)


def tale_add_comment(request, tale_part_id):
    if not request.user.is_authenticated():
        return redirect_with_next('user_add', request.path)
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale_part = TalePart.objects.get(id=tale_part_id, tale__user=profile)
    except TalePart.DoesNotExist:
        return redirect('error_info', _('Tale part not found'))
    if profile.comments.all().count() > 0:
        latest_comment = profile.comments.latest('created_at')
        if (timezone.now() - latest_comment.created_at).seconds < settings.TELLER_COMMENT_COOLDOWN:
            return redirect('error_info', _('You should wait approximately %(comment_cd)s minutes before commenting again')
                            % {'comment_cd': settings.TELLER_COMMENT_COOLDOWN/60})

    if request.method == 'POST':
        form = TaleCommentAddForm(data=request.POST)
        if form.is_valid():
            teller_content_parser = TellerContentParser()
            content = form.cleaned_data['content']
            content = teller_content_parser.clean_html(content)
            tale_part_comment = TalePartComment.objects.create(tale_part=tale_part, user=profile,
                                                               content=content)
            if tale_part_comment is None:
                return redirect('error_info', _('Comment could not be created'))
            if request.GET:
                next_link = request.GET['next']
                if next_link == '' or next_link == '/' or next_link is None:
                    return redirect('tale_read_continue', tale_part.tale.slug)
                return HttpResponseRedirect(next_link)
            else:
                return redirect('tale_read_continue', tale_part.tale.slug)
    else:
        form = TaleCommentAddForm()
    context = {'tale_add_comment_form': form, 'tale_part': tale_part}
    return render_with_defaults(request, 'Teller/tale_add_comment.html', context)


def tale_add_variable(request, tale_slug):
    if not request.user.is_authenticated():
        return redirect_with_next('user_add', request.path)
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale = Tale.objects.get(user=profile, slug=tale_slug)
    except Tale.DoesNotExist:
        return redirect('error_info', _('Tale not found'))
    if request.method == 'POST':
        form = TaleVariableAddForm(tale, data=request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            default_value = form.cleaned_data['default_value']
            if TaleVariable.objects.filter(tale=tale).count() >= settings.TELLER_MAX_VARIABLES_PER_TALE:
                return redirect('error_info', _('Tales can contain maximum of %(max_vars_per_tale)s variables') %
                                {'max_vars_per_tale': settings.TELLER_MAX_VARIABLES_PER_TALE})
            tale_variable = TaleVariable.objects.create(name=name,
                                                        default_value=default_value,
                                                        tale=tale)
            if tale_variable is None:
                return redirect('error_info', _('Tale variable could not be created'))
            return redirect('tale_details', tale.slug)
    else:
        form = TaleVariableAddForm(tale)
    context = {'tale_add_variable_form': form,
               'tale': tale}
    context = add_lists_to_context(context, tale)
    return render_with_defaults(request, 'Teller/tale_add_variable.html', context)


def tale_edit_variable(request, tale_variable_id):
    if not request.user.is_authenticated():
        return redirect_with_next('user_add', request.path)
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale_variable = TaleVariable.objects.get(id=tale_variable_id, tale__user=profile)
    except TaleVariable.DoesNotExist:
        return redirect('error_info', _('Tale variable not found'))
    tale = tale_variable.tale
    if request.method == 'POST':
        form = TaleVariableEditForm(tale, tale_variable.name, data=request.POST)
        if form.is_valid():
            tale_variable.name = form.cleaned_data['name']
            tale_variable.default_value = form.cleaned_data['default_value']
            tale_variable.save()
            return redirect('tale_details', tale.slug)
    else:
        form = TaleVariableEditForm(tale, tale_variable.name, tale_variable)
    context = {'tale_edit_variable_form': form, 'tale_variable': tale_variable}
    context = add_lists_to_context(context, tale)
    return render_with_defaults(request, 'Teller/tale_edit_variable.html', context)


def tale_delete_variable(request, tale_variable_id):
    if not request.user.is_authenticated():
        return redirect_with_next('user_add', request.path)
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale_variable = TaleVariable.objects.get(id=tale_variable_id, tale__user=profile)
    except TaleVariable.DoesNotExist:
        return redirect('error_info', _('Tale variable not found'))
    tale = tale_variable.tale
    tale_variable.delete()
    return redirect('tale_details', tale.slug)


def tale_add(request):
    if not request.user.is_authenticated():
        return redirect_with_next('user_add', request.path)
    profile = Profile.objects.get(user__id=request.user.id)
    if request.method == 'POST':
        form = TaleAddForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            language = form.cleaned_data['language']
            is_poll_tale = form.cleaned_data['is_poll_tale']
            slug = slugify(name)
            if Tale.objects.filter(user=profile).count() >= settings.TELLER_MAX_TALES_PER_USER:
                return redirect('error_info', _('You can have a maximum of %(max_tales_per_user)s tales at once') %
                                {'max_tales_per_user': settings.TELLER_MAX_TALES_PER_USER})
            tale = Tale.objects.create(name=name,
                                       language=language,
                                       is_poll_tale=is_poll_tale,
                                       user=profile,
                                       slug=slug)
            if tale is None:
                return redirect('error_info', _('Tale could not be created'))
            tale_part = TalePart.objects.create(tale=tale,
                                                name=_('STARTING PART'),
                                                content=_('&lt;START WRITING YOUR STORY HERE...&gt;'),
                                                is_active=True,
                                                poll_end_date=None,
                                                is_start=True)
            if tale is None:
                return redirect('error_info', _('Starting part could not be created'))
            return redirect('tale_edit_part', tale_part.id)
    else:
        form = TaleAddForm()
    context = {'tale_add_form': form}
    return render_with_defaults(request, 'Teller/tale_add.html', context)


def tale_delete(request, tale_id):
    if not request.user.is_authenticated():
        return redirect_with_next('user_add', request.path)
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
        return redirect_with_next('user_add', request.path)
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale = Tale.objects.get(user=profile, slug=tale_slug)
    except Tale.DoesNotExist:
        return redirect('error_info', _('Tale not found'))
    # tarjan = TarjansCycleDetection(tale.id, tale)
    # tarjan.detect_cycles()
    context = {'tale': tale, 'tale_full_url': request.build_absolute_uri(reverse('tale_read_continue', args=[tale.slug]))}
    context = add_lists_to_context(context, tale)
    return render_with_defaults(request, 'Teller/tale_details.html', context)


def tale_edit_graph(request, tale_slug):
    if not request.user.is_authenticated():
        return redirect_with_next('user_add', request.path)
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale = Tale.objects.get(user=profile, slug=tale_slug)
    except Tale.DoesNotExist:
        return redirect('error_info', _('Tale not found'))
    # tarjan = TarjansCycleDetection(tale.id, tale)
    # tarjan.detect_cycles()
    context = {'tale': tale}
    context = add_lists_to_context(context, tale)
    return render_with_defaults(request, 'Teller/tale_edit_graph.html', context)


def tale_apply_graph(request, tale_slug):
    if not request.user.is_authenticated():
        return HttpResponse(_('User is not authenticated'))
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale = Tale.objects.get(user=profile, slug=tale_slug)
    except Tale.DoesNotExist:
        return redirect('error_info', _('Tale not found'))
    if request.is_ajax():
        json_data = json.loads(request.POST['json_data'])
        try:
            with transaction.atomic():
                parts = json_data['parts']
                links = json_data['links']
                # Step 1: Edit Parts
                for key, value in parts.items():
                    value['tale'] = tale.slug
                    if value['is_new'] and not value['deleted']:
                        part_form = TalePartForm(profile, tale, data=value)
                        if not part_form.is_valid():
                            raise ValueError(part_form.errors.keys()[0] + ": " + part_form.errors.values()[0][0])
                        name = part_form.cleaned_data['name']
                        content = part_form.cleaned_data['content']
                        is_active = part_form.cleaned_data['is_active']
                        poll_end_date = part_form.cleaned_data['poll_end_date']
                        is_start = TalePart.objects.filter(tale=tale, is_start=True).count() == 0
                        if TalePart.objects.filter(tale=tale).count() >= settings.TELLER_MAX_PARTS_PER_TALE:
                            raise ValueError(_('Tales can contain maximum of %(max_parts_per_tale)s parts') %
                                             {'max_parts_per_tale': settings.TELLER_MAX_PARTS_PER_TALE})
                        tale_part = TalePart.objects.create(tale=tale,
                                                            name=name,
                                                            content=content,
                                                            is_active=is_active,
                                                            poll_end_date=poll_end_date,
                                                            is_start=is_start)
                        if tale_part is None:
                            raise ValueError(_('Could not create the tale part'))
                        value['b_id'] = tale_part.id
                    elif not value['deleted']:
                        tale_part = TalePart.objects.get(id=value['b_id'], tale__user=profile)
                        if tale_part is None:
                            raise ValueError(_('Could not find the tale part: ') + value.get('b_id'))
                        part_form = TaleEditPartForm(profile, tale, tale_part.name, data=value)
                        if not part_form.is_valid():
                            raise ValueError(part_form.errors.keys()[0] + ": " + part_form.errors.values()[0][0])
                        tale_part.name = part_form.cleaned_data['name']
                        tale_part.save()
                # Step 2: Delete Links
                for key, value in links.items():
                    if not value['is_new'] and value['deleted']:
                        tale_link = TaleLink.objects.get(id=value['b_id'], tale__user=profile)
                        if tale_link is None:
                            raise ValueError(_('Could not find the tale link: ') + value.get('b_id'))
                        if tale_link.tale.is_poll_tale and Profile.objects.filter(selected_links=tale_link).count() > 0:
                            raise ValueError(_('Poll tale link is voted and cannot be deleted'))
                        tale_link.delete()
                # Step 3: Edit Links
                for key, value in links.items():
                    if value['is_new'] and not value['deleted']:
                        value['source'] = parts[value['source_node']]['b_id']
                        value['destination'] = parts[value['target_node']]['b_id']
                        link_form = TaleLinkAddForm(tale, data=value)
                        if not link_form.is_valid():
                            raise ValueError(link_form.errors.keys()[0] + ": " + link_form.errors.values()[0][0])
                        name = link_form.cleaned_data['name']
                        action = link_form.cleaned_data['action']
                        source = link_form.cleaned_data['source']
                        destination = link_form.cleaned_data['destination']
                        if TaleLink.objects.filter(source=source).count() >= settings.TELLER_MAX_LINKS_PER_PART:
                            raise ValueError(_('Parts can contain maximum of %(max_links_per_part)s links') %
                                             {'max_links_per_part': settings.TELLER_MAX_LINKS_PER_PART})
                        tale_link = TaleLink.objects.create(source=source,
                                                            destination=destination,
                                                            action=action,
                                                            name=name,
                                                            tale=tale)
                        if tale_link is None:
                            raise ValueError(_('Tale link could not be created'))
                        tarjans_cycle_detection = TarjansCycleDetection(tale.id, tale)
                        if tarjans_cycle_detection.detect_cycles():
                            tale_link.delete()
                            raise ValueError(_('Links should not create cycles in the tale'))
                        value['b_id'] = tale_link.id
                    elif not value['deleted']:
                        tale_link = TaleLink.objects.get(id=value['b_id'], tale__user=profile)
                        if tale_link is None:
                            raise ValueError(_('Could not find the tale link: ') + value.get('b_id'))
                        value['source'] = parts[value['source_node']]['b_id']
                        value['destination'] = parts[value['target_node']]['b_id']
                        link_form = TaleLinkEditForm(tale, tale_link.name, data=value)
                        if not link_form.is_valid():
                            raise ValueError(link_form.errors.keys()[0] + ": " + link_form.errors.values()[0][0])
                        tale_link.name = link_form.cleaned_data['name']
                        tale_link.action = link_form.cleaned_data['action']
                        tale_link.source = link_form.cleaned_data['source']
                        tale_link.destination = link_form.cleaned_data['destination']
                        tale_link.save()
                        tarjans_cycle_detection = TarjansCycleDetection(tale.id, tale)
                        if tarjans_cycle_detection.detect_cycles():
                            raise ValueError(_('Links should not create cycles in the tale'))
                # Step 4: Delete Parts
                for key, value in parts.items():
                    if not value['is_new'] and value['deleted']:
                        tale_part = TalePart.objects.get(id=value['b_id'], tale__user=profile)
                        if tale_part.is_start:
                            raise ValueError(_('Starting parts should not be deleted'))
                        if TaleLink.objects.filter(Q(source=tale_part) | Q(destination=tale_part)).count() > 0:
                            raise ValueError(_('Links of the tale part should be deleted first'))
                        tale_part.delete()
        except IntegrityError:
            return HttpResponse(_('An error is occured'))
        except KeyError:
            return HttpResponse(_('Incorrect JSON'))
        except ValueError as e:
            return HttpResponse(_(e.message))
        return HttpResponse('OK')
    else:
        raise Http404


def tale_list(request):
    if not request.user.is_authenticated():
        return redirect_with_next('user_add', request.path)
    profile = Profile.objects.get(user__id=request.user.id)
    list_of_tales = Tale.objects.filter(user=profile)
    context = {'tale_list': list_of_tales}
    return render_with_defaults(request, 'Teller/tale_list.html', context)


def tale_publish(request, tale_id):
    if not request.user.is_authenticated():
        return redirect_with_next('user_add', request.path)
    profile = Profile.objects.get(user__id=request.user.id)
    try:
        tale = Tale.objects.get(user=profile, id=tale_id)
    except Tale.DoesNotExist:
        return redirect('error_info', _('Tale not found'))
    if not tale.is_published:
        tale.is_published = True
        tale.save()
    if request.GET:
        next_link = request.GET['next']
        if next_link == '' or next_link == '/' or next_link is None:
            return redirect('tale_list')
        return HttpResponseRedirect(next_link)
    else:
        return redirect('tale_list')


def tale_rate(request, tale_id, rate_amount):
    if not request.user.is_authenticated():
        return redirect_with_next('user_add', request.path)
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
        return redirect_with_next('user_add', request.path)
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