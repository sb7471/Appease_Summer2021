from django.shortcuts import render
from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializer import UserSeralizer, HealthDynamicSerializer, HealthStaticSerializer
from .models import healthData
from rest_framework.response import Response
from django.http import HttpResponseNotFound, JsonResponse, FileResponse
from rest_framework.decorators import api_view
from .analytics import Analytics
from django.conf import settings
import sys
import tempfile
sys.path.insert(1, '../btpeer_p2p_framework/project_impl')
from user import AppEasePeer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSeralizer

@api_view(['GET'])
def healthStaticView(request,userToken):
    try:
        print(healthData._meta.db_table)
        healthStaticData = healthData.objects.filter(usertoken=userToken)
    except healthData.DoesNotExist:
        return HttpResponseNotFound("not a valid token")
    serializer = HealthStaticSerializer(healthStaticData, many = True)
    return Response(serializer.data)

@api_view(['GET'])
def healthDynamicView(request,userToken):
    try:
        print(healthData._meta.db_table)
        healthDynamicData = healthData.objects.filter(usertoken=userToken)
    except healthData.DoesNotExist:
        return HttpResponseNotFound("not a valid token")
    serializer = HealthDynamicSerializer(healthDynamicData, many = True)
    return Response(serializer.data)
'''
below uses sqlite data (from kafka)
@api_view(['GET'])
def model(request, userToken, intercept, start, end):
    analytics = Analytics()
    value = intercept = 'yes' if True else False
    result = analytics.buildModel(userToken, value, start, end)
    data = {'message': result}
    return JsonResponse(data)

@api_view(['GET'])
def query(request, userToken, param, start, end):
    print('inside query')
    analytics = Analytics()
    result = analytics.queryData(userToken, param, start, end)
    return FileResponse(open('plot.png', 'rb'))


@api_view(['GET'])
def visualize(request, game, feature):
    return
'''

@api_view(['GET'])
def model(request, intercept, start, end):
	print('hello')

	app = AppEasePeer(firstpeer=settings.PEER, maxpeers=settings.MAX_PEERS, serverport=settings.P2P_PORT)
	print('hello')
	result = app.find_model(intercept)

	data = {
		'message': result
	}

	return JsonResponse(data)

@api_view(['GET'])
def query(request, param, start, end):
	start = start.replace("_", "-")
	end = end.replace("_", "-")
	query_param = ','.join([param, start, end])
	app = AppEasePeer(firstpeer=settings.PEER, maxpeers=settings.MAX_PEERS, serverport=settings.P2P_PORT)
	result = app.query_data(query_param)

	data = {
		'message': result
	}
	return JsonResponse(data)

@api_view(['GET'])
def visualize(request, game, feature):
	print('hello')
	app = AppEasePeer(firstpeer=settings.PEER, maxpeers=settings.MAX_PEERS, serverport=settings.P2P_PORT)

	param = ','.join([game, feature])
	visual_bytes = app.visualize(param)
	visual_bytes = bytes.fromhex(visual_bytes)

	fd, path = tempfile.mkstemp()
	with open(path, 'wb') as file:
		file.write(visual_bytes)

	image = open(path, 'rb')
	return FileResponse(image)
