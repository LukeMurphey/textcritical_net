require.config({
    baseUrl: "/media/javascripts",
    paths: {
        jquery: [
            "http://ajax.googleapis.com/ajax/libs/jquery/1.8.1/jquery",
            "libs/jquery"
        ],
        
        jqueryui: [
            "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.23/jquery-ui",
            "libs/jqueryui"
        ],
             
        datatables: [
            "http://cdnjs.cloudflare.com/ajax/libs/datatables/1.9.3/jquery.dataTables",
            "libs/jquery.dataTables"
        ],
        
        bootstrap: [
            "http://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/2.3.1/js/bootstrap",
            "libs/bootstrap"
        ],
        
        store: [
            "libs/store"
        ],
        
        bootbox: [
            "libs/bootbox"
        ],
        
        add2home: [
            "libs/add2home"
        ],
        
        underscore: [
            "http://cdnjs.cloudflare.com/ajax/libs/underscore.js/1.4.3/underscore-min",
            "libs/underscore"
        ],
        
        app: [
            "app"
        ],

        blockui: [
            "libs/jquery.blockUI"
        ],
        
        jasmine: [
            "http://cdnjs.cloudflare.com/ajax/libs/jasmine/1.3.1/jasmine",
            "libs/jasmine"
        ],
        
        jasmine_html: [
            "http://cdnjs.cloudflare.com/ajax/libs/jasmine/1.3.1/jasmine-html",
            "libs/jasmine-html"
        ],
        
        social_share: [
            "libs/socialShare"       
        ]

    },
    shim: {
        jqueryui: ['jquery'],
        datatables: ['jquery'],
        bootstrap: ['jquery'],
        social_share: ['jquery'],
	    underscore: {
	        exports: '_'
	    }
    }
});