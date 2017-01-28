var gulp = require('gulp');
var jshint = require('gulp-jshint');
var watch = require('gulp-watch');
var browserify = require('browserify');
var babelify = require('babelify');
var source = require('vinyl-source-stream');

var srcPath = 'scriptsrc/**/*.js'

/**
 * Lint all js files.
 */
gulp.task('lint', function () {
  gulp.src(srcPath)
    .pipe(jshint('.jshintrc'))
    .pipe(jshint.reporter('jshint-stylish'))
});

/**
 * Watch and lint all js files.
 */
gulp.task('lint:watch', ['lint'], function () {
  gulp.watch(srcPath, ['lint']);
});

/**
 * Build all es6 modules in scriptsrc/apps with browserify/babelify.
 */
gulp.task('build', function(done) {
  [
    'results',
    'search',
    'settings'
  ].forEach(function(entry) {
    browserify('./scriptsrc/apps/' + entry + '.js')
      .transform(babelify)
      .bundle()
      .pipe(source(entry + '.js'))
      .pipe(gulp.dest('static/js/controllers'));
  });
  done();
});

/**
 * Watch and build.
 */
gulp.task('build:watch', ['build'], function () {
  gulp.watch(srcPath, ['build']);
});

/**
 * Watch, then lint and build.
 */
gulp.task('watch', ['lint:watch', 'build:watch']);

/**
 * Same as watch.
 */
gulp.task('default', ['watch']);