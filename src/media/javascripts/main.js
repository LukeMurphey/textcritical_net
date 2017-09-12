require.config({
    baseUrl: "/media/javascripts",
    paths: {
        jquery: [
            "//ajax.googleapis.com/ajax/libs/jquery/1.8.1/jquery",
            "libs/jquery"
        ],
        
        jqueryui: [
            "//ajax.googleapis.com/ajax/libs/jqueryui/1.8.23/jquery-ui",
            "libs/jqueryui"
        ],
             
        datatables: [
            "//cdnjs.cloudflare.com/ajax/libs/datatables/1.10.16/js/jquery.dataTables",
            "libs/jquery.dataTables"
        ],
        
        bootstrap: [
            "//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/2.3.1/js/bootstrap",
            "libs/bootstrap"
        ],
        
        store: [
            "libs/store"
        ],
        
        bootbox: [
            "libs/bootbox"
        ],
        
        underscore: [
            "//cdnjs.cloudflare.com/ajax/libs/underscore.js/1.4.3/underscore-min",
            "libs/underscore"
        ],
        
        app: [
            "app"
        ],

        blockui: [
            "libs/jquery.blockUI"
        ],
        
        jasmine: [
            "//cdnjs.cloudflare.com/ajax/libs/jasmine/1.3.1/jasmine",
            "libs/jasmine"
        ],
        
        jasmine_html: [
            "//cdnjs.cloudflare.com/ajax/libs/jasmine/1.3.1/jasmine-html",
            "libs/jasmine-html"
        ],
        
        jquery_tools: [
            "//cdn.jquerytools.org/1.2.7/full/jquery.tools.min",
            "libs/jquery.tools.min"
        ],
        
        facebook: [
            "//connect.facebook.net/en_US/all"
        ],
        
        flying_focus: [
            "libs/flying-focus"
        ],
        
        highcharts: [
        	"https://code.highcharts.com/highcharts",
        	"libs/highcharts"
        ],
        
        clipboard: [
            "https://cdnjs.cloudflare.com/ajax/libs/clipboard.js/1.5.10/clipboard",
            "libs/clipboard"
        ],

        riot: [
            "libs/riot+compiler"
        ]

    },
    shim: {
        jqueryui: ['jquery'],
        datatables: ['jquery'],
        bootstrap: ['jquery'],
        jasmine_html: ['jasmine'],
        highcharts: {
            exports: "Highcharts",
            deps: ["jquery"]
        },
	    underscore: {
	        exports: '_'
	    },
    	facebook : {
    		export: 'FB'
    	},
    	riot : {
    		export: 'riot'
    	}
    }
});