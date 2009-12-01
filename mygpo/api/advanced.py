#
# This file is part of my.gpodder.org.
#
# my.gpodder.org is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# my.gpodder.org is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with my.gpodder.org. If not, see <http://www.gnu.org/licenses/>.
#

from mygpo.api.basic_auth import require_valid_user
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, Http404, HttpResponseNotAllowed
from mygpo.api.models import Device, Podcast, SubscriptionAction, Episode, EpisodeAction, SUBSCRIBE_ACTION, UNSUBSCRIBE_ACTION, EPISODE_ACTION_TYPES, DEVICE_TYPES
from mygpo.api.json import JsonResponse
from django.core import serializers
from time import mktime
from datetime import datetime
import json
import xml.utils.iso8601


@require_valid_user()
def subscriptions(request, username, device_uid):

    if request.user.username != username:
        return HttpResponseForbidden()

    now = mktime(datetime.now().timetuple())

    if request.method == 'GET':
        try:
            d = Device.objects.get(user=request.user, uid=device_uid)
        except Device.DoesNotExist:
            return Http404('device %s does not exist' % device_uid)

        try:
            since = request.GET['since']
        except KeyError:
            return HttpResponseBadRequest('parameter since missing')

        changes = get_subscription_changes(user, device, since, now)

        return JsonResponse(changes)

    elif request.method == 'POST':
        d = Device.objects.get_or_create(user=request.user, uid=device_uid)

        actions = json.loads(request.POST['data'])
        add = actions['add'] if 'add' in actions else []
        rem = actions['remove'] if 'remove' in actions else []

        update_subscriptions(request.user, d, add, rem)

        return JsonResponse({'timestamp': now})

    else:
        return HttpResponseNotAllowed(['GET', 'POST'])

def update_subscriptions(user, device, add, remove):
    for add in actions['add']:
        p = Podcast.objects.get_or_create(url=add)
        s = SubscriptionAction.objects.create(podcast=p,device=d,action=SUBSCRIBE_ACTION)

    for remove in actions['remove']:
        p = Podcast.objects.get_or_create(url=remove)
        s = SubscriptionAction.objects.create(podcast=p,device=d,action=UNSUBSCRIBE_ACTION)

def get_subscription_changes(user, device, since, until):
    actions = {}
    for a in SubscriptionAction.objects.filter(device=device, timestamp__gt=since).order_by('timestamp'):
        #ordered by ascending date; newer entries overwriter older ones
        actions[a.podcast] = a

    add = []
    remove = []

    for a in actions:
        if a.action == SUBSCRIBE_ACTION:
            add.append(a.podcast.url)
        elif a.action == UNSUBSCRIBE_ACTION:
            remove.append(a.podcast.url)

    return {'add': add, 'remove': remove, 'timestamp': until}

@require_valid_user()
def episodes(request, username):

    if request.user.username != username:
        return HttpResponseForbidden()

    now = mktime(datetime.now().timetuple())

    if request.method == 'POST':
        try:
            actions = json.loads(request.POST['data'])
        except KeyError:
            return HttpResponseBadRequest()

        update_episodes(request.user, actions)
        return HttpResponse()

    else:
        return HttpResponseNotAllowed(['POST'])


def update_episodes(user, actions):
    for e in actions:
        try:
            podcast = Podcast.objects.get(url=e['podcast'])
            episode = Episode.objects.get(podcast=podcast, url=e['episode'])
            action  = e['action']
            if not action in EPISODE_ACTION_TYPES:
                return HttpResponseBadRequest('invalid action %s' % action)
        except:
            return HttpResponseBadRequest('not all required fields (podcast, episode, action) given')

        device = Device.objects.get_or_create(user=user, uid=e['device'], defaults={'name': 'Unknown', 'type': 'other'}) if 'device' in e else None
        timestamp = iso8601.parse(e['timestamp']) if 'timestamp' in e else None
        position = datetime.strptime(e['position'], '%H:%M:%S').time() if 'position' in e else None

        if position and action != 'play':
            return HttpResponseBadRequest('parameter position can only be used with action play')

        EpisodeAction.objects.create(user=user, episode=episode, device=device, action=action, timestamp=timestamp, playmark=position)

@require_valid_user()
def device(request, username, device_uid):

    if request.user.username != username:
        return HttpResponseForbidden()

    if request.method == 'POST':
        d = Device.objects.get_or_create(user=request.user, uid=device_uid)

        data = json.loads(request.POST['data'])

        if 'caption' in data:
            d.name = data['caption']

        if 'type' in data:
            if not data['type'] in DEVICE_TYPES:
                return 
            d.type = data['type']

        d.save()

        return HttpResponse()

    else:
        return HttpResponseNotAllowed(['POST'])


@require_valid_user()
def devices(request, username):

    if request.user.username != username:
        return HttpResponseForbidden()

    if request.method == 'GET':
        devices = []
        for d in Device.objects.filter(user=request.user):
            devices.append({
                'id': d.uid,
                'caption': d.name,
                'type': d.type,
                'subscriptions': Subscription.objects.filter(device=d).count()
            })

        return JsonResponse(devices)

    else:
        return HttpResponseNotAllowed(['GET'])
