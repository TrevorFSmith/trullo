import os
import time
import urllib
import sys
import datetime
import logging
import tempfile
import shutil

logger = logging.getLogger(__name__)

from boto.s3.key import Key
from boto.s3.bucket import Bucket
from boto.exception import S3ResponseError
from boto.s3.connection import S3Connection

from django.conf import settings

def last_modified(directory_path):
	"""Returns the path to the file in the directory which was last modified, or None if the directory is empty."""
	if not os.path.exists(directory_path): raise Exception("No such directory %s" % directory_path)
	if not os.path.isdir(directory_path): raise Exception("Not a directory %s" % directory_path)
	file_paths = [os.path.join(directory_path, path) for path in os.listdir(directory_path)]
	flist = [file_path for file_path in file_paths if not os.path.isdir(file_path)]
	if len(flist) == 0: return None
	for i in range(len(flist)):
		statinfo = os.stat(flist[i])
		flist[i] = (flist[i],statinfo.st_ctime)
	flist.sort(key=operator.itemgetter(1))
	return flist[-1][0]

class BackupError(Exception):
	pass

class BackupManager(object):
	def __init__(self):
		pass
	
	def call_system(self, command):
		if os.system(command) == 0: return True
		print 'FAILED:', command
		return False
	
	def get_db_info(self):
		if not hasattr(settings, 'DATABASES'): raise BackupError('settings.DATABASES is not defined')
		if not settings.DATABASES.has_key('default'): raise BackupError('settings.DATABASES has no default db')
		if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.postgresql_psycopg2': raise BackupError('This command only works with PostgreSQL')
		if settings.DATABASES['default'].has_key('PASSWORD'):
			password = settings.DATABASES['default']['PASSWORD']
		else:
			password = None
		return (settings.DATABASES['default']['USER'], settings.DATABASES['default']['NAME'], password)
	
	def latest_backup(self):
		self.check_dirs()
		return last_modified(settings.BACKUP_ROOT)
	
	def restore_backup(self, file_path):
		backup_path = os.path.realpath(file_path)
		if not os.path.exists(backup_path): raise BackupError('The backup file "%s" does not exist.' % backup_path)
		if not os.path.isfile(backup_path): raise BackupError('The specified backup file "%s" is not a file.' % backup_path)
		if not backup_path.endswith('.tar'): raise BackupError('The specified backup file "%s" must be a tar file.' % backup_path)

		self.check_dirs()
		db_user, db_name, db_password = self.get_db_info()

		logger.debug('Restoring from backup file "%s"' % backup_path)

		# create the working directory
		working_dir = tempfile.mkdtemp('backup-temp')

		# untar the backup file, which should result in two files: sql and media
		command = 'cd "%s" && tar -xzf "%s"' % (working_dir, backup_path)
		if not self.call_system(command): raise BackupError('Aborting restoration.')

		# create a sub directory for the media, and untar it
		command = 'cd "%s" && tar -xzf %s/*-media.tgz' % (working_dir, working_dir)
		if not self.call_system(command): raise BackupError('Aborting restoration.')

		# move each media dir from the temp media dir into the project media dir
		media_dir = os.path.join(working_dir, 'media')
		if not os.path.exists(media_dir): raise BackupError('Could not restore the media dir')
		for media_file in os.listdir(media_dir):
			target = os.path.join(settings.MEDIA_ROOT, media_file)
			if os.path.exists(target) and os.path.isdir(target): shutil.rmtree(target)
			if os.path.exists(target): os.remove(target)
			shutil.move(os.path.join(media_dir, media_file), target)

		if db_password: os.environ['PGPASSWORD'] = db_password

		# now delete and recreate the database
		command = 'echo "drop database %s; create database %s;" | psql -U %s' % (db_name, db_name, db_user)
		if not self.call_system(command): raise BackupError('Aborting restoration.')

		# gunzip the db dump
		command = 'cd "%s" && gunzip *-sql.gz' % working_dir
		if not self.call_system(command): raise BackupError('Aborting restoration.')

		# restore database
		command = 'cd "%s" && pg_restore -n public -d %s -U %s *-sql' % (working_dir, db_name, db_user)
		if not self.call_system(command): raise BackupError('Aborting restoration.')

		# restore permissions
		command = 'echo "grant all on all tables in schema public to %s; grant all on all sequences in schema public to %s; grant all on all functions in schema public to %s;" | psql -U %s' % (db_user, db_user, db_user, db_user)
		if not self.call_system(command): raise BackupError('Aborting restoration.')

	def check_dirs(self):
		if not hasattr(settings, 'MEDIA_ROOT'): raise BackupError('The MEDIA_ROOT is not defined')
		if not os.path.exists(settings.MEDIA_ROOT): raise BackupError('MEDIA_ROOT "%s" does not exist.' % settings.MEDIA_ROOT)
		if not os.path.isdir(settings.MEDIA_ROOT): raise BackupError('MEDIA_ROOT "%s" is not a directory.' % settings.MEDIA_ROOT)

		if not hasattr(settings, 'BACKUP_ROOT'): raise BackupError('You must define BACKUP_ROOT in settings.py')
		if not os.path.exists(settings.BACKUP_ROOT): os.makedirs(settings.BACKUP_ROOT)
		if not os.path.exists(settings.BACKUP_ROOT): raise BackupError('Backup root "%s" does not exist' % settings.BACKUP_ROOT)
		if not os.path.isdir(settings.BACKUP_ROOT): raise BackupError('Backup root "%s" is not a directory' % settings.BACKUP_ROOT)
	
	def make_backup(self):
		self.check_dirs()
		db_user, db_name, db_password = self.get_db_info()

		now = datetime.datetime.now()
		file_token = '%d-%02d-%02d_%02d-%02d-%02d' % (now.year, now.month, now.day, now.hour, now.minute, now.second)

		sql_file = '%s-sql.gz' % file_token
		sql_path = '%s/%s' % (settings.BACKUP_ROOT, sql_file)
		sql_pass_args = ''
		if db_password: os.environ['PGPASSWORD'] = db_password
		command = 'pg_dump -Fc --no-acl --no-owner -U %s %s | gzip > "%s"' % (db_user, db_name, sql_path)
		if not self.call_system(command):
			print 'aborting'
			return

		media_file = '%s-media.tgz' % file_token
		media_path = '%s/%s' % (settings.BACKUP_ROOT, media_file)
		command = 'cd "%s" && cd .. && tar -czf "%s" "%s"' % (settings.MEDIA_ROOT, media_path, settings.MEDIA_ROOT.split('/')[-1])
		if not self.call_system(command):
			print 'aborting'
			return

		
		backup_file = '%s-backup.tar' % file_token
		backup_path = '%s/%s' % (settings.BACKUP_ROOT, backup_file)
		print 'backup_file', backup_file, backup_path
		command = 'cd "%s" && tar -czf "%s" "%s" "%s"' % (settings.BACKUP_ROOT, backup_path, media_file, sql_file)
		if not self.call_system(command):
			print 'aborting'
			return

		if not self.call_system('cd "%s" && ln -fs "%s" latest-backup.tar' % (settings.BACKUP_ROOT, backup_file)):
			print 'Could not link %s to latest-backup.tar' % backup_file
			
		command = 'rm -f "%s" "%s"' % (media_path, sql_path)
		if not self.call_system(command): print 'Could not erase temp backup files'

		
		return os.path.join(settings.BACKUP_ROOT, backup_path)

class S3Util(object):

	def __init__(self, access_key, secret_key):
		self.access_key = access_key
		self.secret_key = secret_key

	def write_files_to_bucket(self, bucket_name, file_paths):
		for file_path in file_paths:
			if not os.path.isfile(file_path): raise BackupError('%s does not exist' % file_path)

		connection = S3Connection(self.access_key, self.secret_key)
		try:
			bucket = connection.get_bucket(bucket_name)
		except S3ResponseError:
			raise BackupError('Could not read bucket: %s' % bucket_name)

		for file_path in file_paths:
			key = Key(bucket)
			key.key = os.path.basename(file_path)
			key.set_contents_from_filename(file_path)

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
