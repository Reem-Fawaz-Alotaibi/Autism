import json
from django.shortcuts import render, get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder
from ai_analysis.models import Activity


def activity_list(request):
    visual   = Activity.objects.filter(category='visual',   is_active=True)
    sensory  = Activity.objects.filter(category='sensory',  is_active=True)
    motor    = Activity.objects.filter(category='motor',    is_active=True)
    language = Activity.objects.filter(category='language', is_active=True)

    conv_id = None
    if request.user.is_authenticated:
        from chatbot.models import Conversation
        conv, _ = Conversation.objects.get_or_create(user=request.user)
        conv_id = conv.id

    return render(request, 'activity/activity_list.html', {
        'visual':        visual,
        'sensory':       sensory,
        'motor':         motor,
        'language':      language,
        'visual_json':   json.dumps(list(visual.values('id','title','emoji','description','tag','level')),   cls=DjangoJSONEncoder),
        'sensory_json':  json.dumps(list(sensory.values('id','title','emoji','description','tag','level')),  cls=DjangoJSONEncoder),
        'motor_json':    json.dumps(list(motor.values('id','title','emoji','description','tag','level')),    cls=DjangoJSONEncoder),
        'language_json': json.dumps(list(language.values('id','title','emoji','description','tag','level')), cls=DjangoJSONEncoder),
        'conv_id':       conv_id,
    })


def activity_play(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id, is_active=True)
    return render(request, f'activity/{activity.html_file}', {'activity': activity})