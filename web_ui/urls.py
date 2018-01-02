"""
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
"""
URL mapping of the application
"""

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^download/(?P<file_name>.*)/?$', views.downloads, name='downloads'),

    url(r'^$', views.index, name='index'),

    # Angular mappings
    url(r'^home/?$', views.index, name='home'),
    url(r'^ng/home/?$', views.home, name='home'),

    url(r'^snapshot/?$', views.index, name='snapshot'),
    url(r'^ng/snapshot/?$', views.snapshot, name='snapshot'),

    # APIs Mappings
    url(r'^api/login/get_token/?$', views.api_get_token, name='api_get_token'),
    url(r'^api/pod/?$', views.api_pod, name='api_pod'),
    url(r'^api/switch/get/?$', views.api_switch, name='api_switch'),
    url(r'^api/snapshot/?$', views.api_take_snapshot, name='api_take_snapshot'),
    url(r'^api/diff/?$', views.api_get_diff, name='api_get_diff'),
    url(r'^api/files/?$', views.api_files, name='api_files'),
]
