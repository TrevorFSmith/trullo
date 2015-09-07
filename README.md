# Trullo: vanity sites for maker types.

Trullo is a Django web application written in Python.

# Installation

	git clone git://github.com/TrevorFSmith/trullo.git
	cd trullo
	npm install
	pip install -r requirements.txt
	cp trullo/local_settings.example trullo/local_settings.py

Then, edit local_settings.py to reflect your local environment.

# Running

To run Grunt to compile the front-end:

	grunt

To run the Django dev server on your [local machine](http://127.0.0.1:8000/):

	./manage.py runserver 0.0.0.0:8000

# License

Trullo is Copyright 2012 [Trevor F. Smith](http://trevor.smith.name/).

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0). Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
