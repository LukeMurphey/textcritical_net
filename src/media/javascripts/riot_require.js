define([
    'jquery',
    'underscore',
    'highcharts',
    'riot'
],
function($, _, highcharts, riotjs) {
    console.log("Loading riotjs");

    if(typeof riot === "undefined"){
        // Put riot in the global scope so that the created tags can see it
        riot = riotjs;
    }

    return riot;
});
