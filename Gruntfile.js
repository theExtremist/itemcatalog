module.exports = function(grunt) {

  grunt.initConfig({
    /* Post-css prefixes */
    postcss: {
        options: {
        map: true,
        processors: [
          require('autoprefixer')({browsers: ['last 2 version']})
    ]
  },
        dist: {
            src: 'static/*.css'
        }
    }
  });


  grunt.loadNpmTasks('grunt-postcss');
  grunt.registerTask('default', ['postcss']);

};
