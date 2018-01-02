from __future__ import unicode_literals
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
import traceback
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from web_ui.controllers.apic import ApicController, SNAPSHOT_PATH
from web_ui.controllers import diff
import glob
import os
from django.utils.encoding import smart_str


# ====================>>>>>>>> Utils <<<<<<<<====================
class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


# ====================>>>>>>>> Templates <<<<<<<<====================
def index(request):
    return render(request, 'web_app/index.html')


def home(request):
    return render(request, 'web_app/home.html')


def snapshot(request):
    return render(request, 'web_app/snapshot.html')


# ====================>>>>>>>> APIs <<<<<<<<====================
@csrf_exempt
def api_get_token(request):
    """
    Return an APIC token to be used by the web client
    :param request:
    :return:
    """
    if request.method == 'POST':
        try:

            # Parse the json
            payload = json.loads(request.body)
            apic = ApicController()
            apic.url = payload["apic"]["url"]
            request.session['apic_url'] = payload["apic"]["url"]
            payload["apic"]["token"] = apic.get_token(username=payload["apic"]["username"],
                                                      password=payload["apic"]["password"])
            return JSONResponse(payload)
        except Exception as e:
            print(traceback.print_exc())
            # return the error to web client
            return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)
    else:
        return JSONResponse("Bad request. " + request.method + " is not supported", status=400)


@csrf_exempt
def api_pod(request):
    """
       Return a list of pods
       :param request:
       :return:
       """
    if 'HTTP_AUTHORIZATION' in request.META:
        apic_token = request.META['HTTP_AUTHORIZATION'].split(' ')[1]
        apic_url = request.META['HTTP_AUTHORIZATION'].split(' ')[2]
        if request.method == 'GET':
            try:
                apic = ApicController()
                apic.url = apic_url
                apic.token = apic_token
                pods = apic.getPods()
                return JSONResponse(pods)
            except Exception as e:
                print(traceback.print_exc())
                # return the error to web client
                return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)
        else:
            return JSONResponse("Bad request. " + request.method + " is not supported", status=400)

    else:
        return JSONResponse("Bad request. HTTP_AUTHORIZATION header is required", status=400)


@csrf_exempt
def api_switch(request):
    """
       Return a list of switches
       :param request:
       :return:
       """
    if 'HTTP_AUTHORIZATION' in request.META:
        apic_token = request.META['HTTP_AUTHORIZATION'].split(' ')[1]
        apic_url = request.META['HTTP_AUTHORIZATION'].split(' ')[2]
        if request.method == 'POST':
            try:
                payload = json.loads(request.body)
                apic = ApicController()
                apic.url = apic_url
                apic.token = apic_token
                switches = apic.getSwitches(pod_dn=payload["pod"]["fabricPod"]["attributes"]["dn"])
                return JSONResponse(switches)
            except Exception as e:
                print(traceback.print_exc())
                # return the error to web client
                return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)
        else:
            return JSONResponse("Bad request. " + request.method + " is not supported", status=400)
    else:
        return JSONResponse("Bad request. HTTP_AUTHORIZATION header is required", status=400)


@csrf_exempt
def api_take_snapshot(request):
    """
    Take the snapshot of the switch and saves it in a local database
    :param request:
    :return:
    """
    if 'HTTP_AUTHORIZATION' in request.META:
        apic_token = request.META['HTTP_AUTHORIZATION'].split(' ')[1]
        apic_url = request.META['HTTP_AUTHORIZATION'].split(' ')[2]
        if request.method == 'POST':
            try:
                payload = json.loads(request.body)
                apic = ApicController()
                apic.url = apic_url
                apic.token = apic_token
                apic.saveSnapshot(switch_dn=payload["switch"]["fabricNode"]["attributes"]["dn"],
                                  filename=payload["snapshot"]["name"],
                                  type=payload["snapshot"]["type"])
                return JSONResponse("ok")
            except Exception as e:
                print(traceback.print_exc())
                # return the error to web client
                return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)
        else:
            return JSONResponse("Bad request. " + request.method + " is not supported", status=400)
    else:
        return JSONResponse("Bad request. HTTP_AUTHORIZATION header is required", status=400)


@csrf_exempt
def api_get_diff(request):
    """
    Returns the diff of two files
    :param request:
    :return:
    """
    if 'HTTP_AUTHORIZATION' in request.META:
        apic_url = request.META['HTTP_AUTHORIZATION'].split(' ')[2]
        if request.method == 'POST':
            try:
                payload = json.loads(request.body)
                diff_str = diff.getDiff(file_name_1=payload["files"][0]["name"],
                                        file_name_2=payload["files"][1]["name"],
                                        apic_url=apic_url)
                return JSONResponse({"diff": diff_str})
            except Exception as e:
                print(traceback.print_exc())
                # return the error to web client
                return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)
        else:
            return JSONResponse("Bad request. " + request.method + " is not supported", status=400)
    else:
        return JSONResponse("Bad request. HTTP_AUTHORIZATION header is required", status=400)


@csrf_exempt
def api_files(request):
    """
    Returns the files from a comparison
    :param request:
    :return:
    """
    if 'HTTP_AUTHORIZATION' in request.META:
        apic_url = request.META['HTTP_AUTHORIZATION'].split(' ')[2]
        if request.method == 'GET':
            result = []
            try:
                apic_dir = apic_url.replace("http:", "").replace("https:", "").replace("/", "") + "/"
                if os.path.isdir(SNAPSHOT_PATH + "/" + apic_dir):
                    files = glob.glob(
                        SNAPSHOT_PATH + "/" + apic_url.replace("http:", "").replace("https:", "").replace("/",
                                                                                                          "") + "/*")
                    for file_path in files:
                        result.append({"name": file_path.split("/")[len(file_path.split("/")) - 1]})
                return JSONResponse(result)
            except Exception as e:
                print(traceback.print_exc())
                # return the error to web client
                return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)
        else:
            return JSONResponse("Bad request. " + request.method + " is not supported", status=400)
    else:
        return JSONResponse("Bad request. HTTP_AUTHORIZATION header is required", status=400)


def downloads(request, file_name):
    """
    Downloads a requested file
    :param request:
    :param file_name:
    :return:
    """
    try:
        response = HttpResponse(
            content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name + '.txt')
        with open(SNAPSHOT_PATH + "/" + file_name, 'r') as config_file:
            data = config_file.read()
            response.write(data)
        return response
    except Exception as e:
        # return the error to web client
        return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)
