<workindexdialog>
    <div class={ hide: !show, workindexmodal: true }>
        <workindex page_length=5 wait_to_render>
            Loading list of works...
        </workindex>
    </div>

    <style>
        .workindexmodal{
            width: 600px;
            position: fixed;
            background-color: #2f2f2f;
            z-index: 100;
            border: 2px solid #333;
            padding: 20px;
            box-shadow: 5px 5px 5px #222;
        }
    </style>
    <script>

        this.show = false;
        this.mounted = false;

        // Run the functions as necessary on mount.
        this.on('mount', function(){
            // Link up to the observable
            if(this.opts.observable){
                this.opts.observable.on('open-library-modal', function() {
                    if(!this.mounted){
                        this.tags.workindex.getWorks();
                        this.mounted = true;
                    }

                    this.showDialog();
                }.bind(this));
            }
            else{
                console.warn('Observable was empty; will not be able to monitor for the calls to open the library list dialog');
            }
        });

        // Show the library dialog.
        showDialog(){
            this.show = true;
            this.update();
        }
    </script>
</workindexdialog>