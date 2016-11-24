module.exports = function(grunt) {

  grunt.initConfig({
    /* Post-css prefixes */
    postcss: {
        options: {
            map: true,
            processors: [
                require('autoprefixer')({
                    browsers: ['last 2 versions']
                })
            ]
        },
        dist: {
            src: 'css/*.css'
        }
    }
  });


  grunt.loadNpmTasks('grunt-postcss');
  grunt.registerTask('default', ['postcss']);

};
