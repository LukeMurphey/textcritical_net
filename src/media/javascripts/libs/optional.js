/**
 * RequireJS plugin for optional module loading.
 * From: http://xion.io/post/code/requirejs-optional.html
 */
define ([], function() {


/** Default value to return when a module failed to load. */
var DEFAULT = null;

function load(moduleName, parentRequire, onload) {
    parentRequire([moduleName], onload, function (err) {
        var failedModule = err.requireModules && err.requireModules[0];
        console.warn("Could not load optional module: " + failedModule);
        requirejs.undef(failedModule);

        define(failedModule, [], function() { return DEFAULT; });
        parentRequire([failedModule], onload);
    });
}

return {
    load: load,
};

});