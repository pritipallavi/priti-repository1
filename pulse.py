#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from models.organization import Organization


class PulseHandler(webapp2.RequestHandler):
    def get(self):

        id = self.request.get_all('id')[0]
        org = int(self.request.get_all('org')[0])

        h = Organization.get_by_id(org).get_heart(id)
        h.registerPulse()

        self.response.write('ok')

app = webapp2.WSGIApplication([
    ('/pulse.*', PulseHandler)
], debug=True)
