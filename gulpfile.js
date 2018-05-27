const _ = require('lodash');
const gulp = require('gulp');
const livereload = require('livereload');
const open = require('open');
const os = require('os');
const path = require('path');
const runSequence = require('run-sequence');

/* -----------------------------------------------------------------------------
 * Config
 ---------------------------------------------------------------------------- */

const gulpConfig = require('./gulp.config');

const livereloadOpen =
  (gulpConfig.webserver.https ? 'https' : 'http') +
  '://' +
  gulpConfig.webserver.host +
  ':' +
  gulpConfig.webserver.port +
  (gulpConfig.webserver.open ? gulpConfig.webserver.open : '/');

/* -----------------------------------------------------------------------------
 * Misc
 ---------------------------------------------------------------------------- */

const flags = {
  livereloadInit: false // Whether `livereload-init` task has been run
};
let server;

// Choose browser for node-open.
let browser = gulpConfig.webserver.browsers.default;
const platform = os.platform();
if (_.has(gulpConfig.webserver.browsers, platform)) {
  browser = gulpConfig.webserver.browsers[platform];
}

/* -----------------------------------------------------------------------------
 * Functions
 ---------------------------------------------------------------------------- */

/**
 * Start a watcher.
 *
 * @param {Array} files
 * @param {Array} tasks
 * @param {boolean} livereload - Set to `true` to force livereload to refresh the page.
 */
function startWatch(files, tasks, livereload) {
  if (livereload) {
    tasks.push('livereload-reload');
  }

  gulp.watch(files, function() {
    runSequence(...tasks);
  });
}

/* -----------------------------------------------------------------------------
 * Tasks
 ---------------------------------------------------------------------------- */

gulp.task('build', function(cb) {
  cb();
});

// Start the LiveReload server.
gulp.task('livereload-init', function(cb) {
  if (!flags.livereloadInit) {
    flags.livereloadInit = true;
    server = livereload.createServer();
    open(livereloadOpen, browser);
  }
  cb();
});

// Refresh the page.
gulp.task('livereload-reload', function(cb) {
  server.refresh(livereloadOpen);
  cb();
});

gulp.task('watch:livereload', function() {
  const livereloadTask = 'livereload-reload';
  const watchTasks = [
    {
      files: [
        path.join('app/templates', '*.jinja2'),
        path.join('app/views', '*.py')
      ],
      tasks: ['build']
    }
  ];

  _.forEach(watchTasks, function(watchConfig) {
    const tasks = _.clone(watchConfig.tasks);
    tasks.push(livereloadTask);
    startWatch(watchConfig.files, tasks);
  });
});

gulp.task('livereload', function() {
  runSequence('livereload-init', 'watch:livereload');
});

gulp.task('open', function() {
  return open(livereloadOpen, browser);
});

/* -----------------------------------------------------------------------------
 * Default task
 ---------------------------------------------------------------------------- */

gulp.task('default', ['livereload']);
