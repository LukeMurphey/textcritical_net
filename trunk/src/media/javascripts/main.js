require.config({
    baseUrl: "media/javascripts",
    paths: {
        jquery: [
            "http://ajax.googleapis.com/ajax/libs/jquery/1.8.1/jquery",
            "libs/jquery-1.7.1"
        ],
        jqueryui: [
            "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.23/jquery-ui",
            "libs/jqueryui"
        ],
             
        datatables: [
            "http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.3/jquery.dataTables",
            "libs/jquery.dataTables"
        ],
        
        bootstrap: [
            "libs/bootstrap"
        ]
    },
    shim: {
        'jqueryui': ['jquery'],
        'datatables': ['jquery'],
        'bootstrap': ['jquery']
    }
});
