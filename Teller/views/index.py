import datetime
from Teller.models import Tale, TalePart
from Teller.shortcuts.teller_shortcuts import render_with_defaults
from django.utils import timezone
from django.db.models import Avg
from django.utils.translation import ugettext as _


def index(request):
    start_date = timezone.now() - datetime.timedelta(days=30)
    end_date = timezone.now()
    best_recent_tales = Tale.objects.filter(
        ratings__created_at__range=[start_date, end_date]
    ).annotate(
        recent_avg_rating=Avg('ratings__rating')
    ).order_by(
        '-recent_avg_rating'
    )
    if best_recent_tales.count() == 0:
        best_recent_tales = Tale.objects.all()
    best_recent_tale_part = TalePart.objects.filter(tale=best_recent_tales[0], is_start=True)
    if best_recent_tale_part.count() > 0:
        best_recent_tale_content = best_recent_tale_part[0].content
    else:
        best_recent_tale_content = _('No content yet...')

    freshly_written_tale = Tale.objects.latest('created_at')
    freshly_written_tale_part = TalePart.objects.filter(tale=freshly_written_tale, is_start=True)
    if freshly_written_tale_part.count() > 0:
        freshly_written_tale_content = freshly_written_tale_part[0].content
    else:
        freshly_written_tale_content = _('No content yet...')

    try:
        nearest_time_poll_part = TalePart.objects.filter(poll_end_date__gt=end_date, tale__is_poll_tale=True).earliest(
            'poll_end_date')
        nearest_time_poll = nearest_time_poll_part.tale
    except TalePart.DoesNotExist:
        nearest_time_poll = None
        nearest_time_poll_part = None

    context = {
        'best_recent_tale': best_recent_tales[0],
        'best_recent_tale_content': best_recent_tale_content,
        'freshly_written_tale': freshly_written_tale,
        'freshly_written_tale_content': freshly_written_tale_content,
        'nearest_time_poll_tale': nearest_time_poll,
        'nearest_time_poll_part': nearest_time_poll_part,
    }

    return render_with_defaults(request, 'Teller/index.html', context)


def index_about(request):
    return render_with_defaults(request, 'Teller/about.html', {})