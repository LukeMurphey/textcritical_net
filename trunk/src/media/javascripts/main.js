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
            "http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.3/jquery.dataTables",
            "libs/jquery.dataTables"
        ],
        
        qunit: [
            "http://code.jquery.com/qunit/qunit-1.10.0",
            "libs/qunit"
        ],
        
        bootstrap: [
            "libs/bootstrap"
        ],
        
        store: [
             "libs/store"
        ],
        
        bootbox: [
             "libs/bootbox"
        ],
        
        underscore: [
             "http://cdnjs.cloudflare.com/ajax/libs/underscore.js/1.4.3/underscore-min",
             "libs/underscore"
        ],
        
        app: [
             "app"
        ]
    },
    shim: {
        'jqueryui': ['jquery'],
        'datatables': ['jquery'],
        'bootstrap': ['jquery']
    }
});
