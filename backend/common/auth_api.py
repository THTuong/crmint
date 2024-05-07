# Copyright 2020 Google Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from flask import Flask, request, abort


# Define your bearer token
BEARER_TOKEN = "testkey"

# Function to check bearer token
def check_auth(token):
    return token == BEARER_TOKEN


def add(app):
  # pylint: disable=unused-variable,inconsistent-return-statements
  @app.before_request
  def require_auth():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        abort(401, 'Authorization header is missing')
    
    auth_type, token = auth_header.split(None, 1)
    
    if auth_type.lower() != 'bearer':
        abort(401, 'Invalid authentication type')
    
    if not check_auth(token):
        abort(401, 'Invalid bearer token')
