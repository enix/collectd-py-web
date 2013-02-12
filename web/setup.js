({
    appDir: ".",
    dir: "../collectdweb/share/web",
    baseUrl : './media/js/',
    mainConfigFile : './media/js/config.js',
    fileExclusionRegExp : /(^\.|optimized|build|test|node_modules|js-cov|setup)/,
    findNestedDependencies: true,
    removeCombined: true,
    uglify: {
        max_line_length: 500
        },
    modules : [
        {
        name: "main"
    }, {
        name: "extern"
    }
    ]
})
