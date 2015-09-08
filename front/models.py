from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.OneToOneField(User, unique=True)
	about = models.TextField(blank=True)
	contact = models.TextField(blank=True)
	image = models.ImageField(upload_to='user_profile_image', blank=True, null=True)
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

# Copyright 2012 Trevor F. Smith (http://trevor.smith.name/) 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
