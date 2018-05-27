module.exports = {
  webserver: {
    host: 'localhost',
    port: 8080,
    path: '/',
    livereload: false,
    directoryListing: false,
    open: '/',
    https: false,
    browsers: {
      default: 'firefox',
      darwin: 'google chrome',
      linux: 'google-chrome',
      win32: 'chrome'
    }
  }
};
