<workindexdialog>
    <div class={ hide: !show, workindexmodal: true, container: false }>
        <h3 class="popover-title">Library
            <button type="button" class="close" onclick={ closeDialog } aria-hidden="true">×</button>
        </h3>
        <div class="workindexcontent">
            <workindex page_length=5 wait_to_render readworkurl={ readworkurl } searchurl={ searchurl }>
                <div class="worksloading">
                Loading list of works...
                </div>
            </workindex>
        </div>
    </div>

    <style>
        .workindexmodal{
            /* width: 700px; */
            position: fixed;
            background: #2f2f2f;
            z-index: 100;
            /*
            border-radius: 5px 5px 0 0;
            border-bottom: 1px solid #ebebeb;
            */
            -webkit-border-radius: 5px 5px 0 0;
            -moz-border-radius: 5px 5px 0 0;

            border: 1px solid rgba(0, 0, 0, 0.5);
            border: 1px solid #444;
            -webkit-border-radius: 6px;
            -moz-border-radius: 6px;
            border-radius: 6px;
            -webkit-box-shadow: 0 5px 10px rgba(0, 0, 0, 0.4);
            -moz-box-shadow: 0 5px 10px rgba(0, 0, 0, 0.4);
            box-shadow: 0 5px 10px rgba(0, 0, 0, 0.4);
            -webkit-background-clip: padding-box;
            -moz-background-clip: padding;
            background-clip: padding-box;
        }

        .workindexcontent{
            padding: 0 20px 0px 20px;
        }

        .worksloading{
            padding: 60px 60px 60px 60px;
        }
    </style>
    <script>

        this.show = false;
        this.mounted = false;

        // Get the parameters that will be pased down to the workindex tag
        this.searchurl = this.opts.searchurl;
        this.readworkurl = this.opts.readworkurl;

        // Run the functions as necessary on mount.
        this.on('mount', function(){
            // Link up to the observable
            if(this.opts.observable){

                // Listen for requests to open the library dialog
                this.opts.observable.on('open-library-modal', function() {
                    if(!this.mounted){
                        this.tags.workindex.getWorks();
                        this.mounted = true;
                    }

                    this.showDialog();
                }.bind(this));

                // Listen for requests to close the library dialog
                this.opts.observable.on('close-library-modal', function() {
                    this.closeDialog();
                });
            }
            else{
                console.warn('Observable was empty; will not be able to monitor for the calls to open the library list dialog');
            }
        });

        /*
         * Show the library dialog.
         */
        showDialog(){
            this.show = true;
            this.update();
        }

        /*
         * Close the dialog.
         */
        closeDialog(){
            this.show = false;
            this.update();
        }
    </script>
</workindexdialog>