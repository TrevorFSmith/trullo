module.exports = function(grunt) {

	// This will hold all files and directories to clean with the 'clean' task
	var cleanFiles = ['trullo/static/compiled/'];

	// This will hold all of the sass file data structures
	var lessFiles = [{
						'expand': true,
						'cwd': 'trullo/static',
						'src': ['**/*.less', '!**/_*.less', '!bootstrap-3.3.5/**'],
						'dest': 'trullo/static/compiled/',
						'ext': '.css'
					}];

	var cssFiles = [{
						'expand': true,
						'cwd': 'trullo/static/compiled/',
						'src': ['**/*.css', '!**/*.min.css'],
						'dest': 'trullo/static/compiled/',
						'ext': '.min.css'
					}];

	// These are the names of Django app directories with compilation needs
	var appDirs = ['front', 'publish', 'staff'];

	// For each app directory, update the lessFiles, cssFiles, and cleanFiles
	for(i = 0; i < appDirs.length; i++){
		var currentWorkingDirectory = appDirs[i] + '/static/' + appDirs[i] + '/';
		var destination = currentWorkingDirectory + 'compiled/'
		lessFiles[lessFiles.length] = {
			'expand': true,
			'cwd': currentWorkingDirectory,
			'src': ['**/*.less', '!**/_*.less'],
			'dest': destination,
			'ext': '.css'
		};

		cssFiles[cssFiles.length] = {
			'expand': true,
			'cwd': destination,
			'src': ['**/*.css', '!**/*.min.css'],
			'dest': destination
		}

		cleanFiles[cleanFiles.length] = destination;
	}

	grunt.initConfig({
		'pkg': grunt.file.readJSON('package.json'),
		'clean': {
			'src': cleanFiles
		},
		'less': {
			'development': {
				'options': {
					'compress': true,
					'yuicompress': true,
					'optimization': 2
				},
				'files':lessFiles
			}
		},
		'watch': {
			'all': {
				'options': { 'spawn': false, 'interrupt':false, 'atBegin':true },
				'files': ['**/*.less'],
				'tasks': ['less']
			},
		}
	});

	grunt.loadNpmTasks('grunt-contrib-clean');
	grunt.loadNpmTasks('grunt-contrib-less');
	grunt.loadNpmTasks('grunt-contrib-watch');

	grunt.registerTask('default', ['less']);
};