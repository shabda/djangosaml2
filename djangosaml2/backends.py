# Copyright (C) 2010 Yaco Sistemas (http://www.yaco.es)
# Copyright (C) 2009 Lorenzo Gil Sanchez
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class Saml2Backend(ModelBackend):

    def authenticate(self, session_info=None):
        if session_info is None:
            return None

        if not 'ava' in session_info:
            return None

        ava = session_info['ava']
        username = ava[settings.SAML_USERNAME_ATTRIBUTE][0]

        modified = False
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create(username=username, password='')
            modified = True

        modified = modified or self._update_user_attributes(user, ava)

        if modified:
            user.save()

        return user

    def _update_user_attributes(self, user, attributes):
        """Update the Django user attributes.

        By default it uses a mapping defined in the settings constant
        SAML_ATTRIBUTE_MAPPING.

        This method should not save the user object. The caller will
        do it the return value is True.

        This returns True if the user was modified or False otherwise.
        """
        if not hasattr(settings, 'SAML_ATTRIBUTE_MAPPING'):
            return False

        modified = False
        for saml_attr, django_attr in settings.SAML_ATTRIBUTE_MAPPING.items():
            try:
                setattr(user, django_attr, attributes[saml_attr][0])
                modified = True
            except KeyError:
                # the saml attribute is missing
                pass

        return modified
