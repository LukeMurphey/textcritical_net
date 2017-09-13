<workindexdialog>
    <div class={ hide: !show, workindexmodal: true, container: true }>
        <h3 class="pull-left">Library</h3><button type="button" class="close pull-right" onclick={ closeDialog }>×</button>
        <div class="workindexcontent">
            <workindex page_length=5 wait_to_render readworkurl={ readworkurl } searchurl={ searchurl }>
                <div class="worksloading">
                Loading list of works...
                </div>
            </workindex>
        </div>
    </div>

    <style>


        button.close{
            color: white;
            font-size: 34px;
            margin-top: 16px;
            margin-left: 16px;
            opacity: .3;
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
        this.hidewhenopen = this.opts.hidewhenopen;

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

            if(this.hidewhenopen){
                $(this.hidewhenopen).hide();
            }
        }

        /*
         * Close the dialog.
         */
        closeDialog(){
            this.show = false;
            this.update();
            if(this.hidewhenopen){
                $(this.hidewhenopen).show();
            }
        }
    </script>
</workindexdialog>