<modaldialog>

    <div style="display:none" ref="dialog" class="mymodal modal hide fade" tabindex="-1" role="dialog" aria-labelledby="popup-dialog-label" aria-hidden="true">
        <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
            <h3>{ opts.title }</h3>
        </div>
        <div class="modal-body">
            <yield from="body"/>
        </div>
        <div class="modal-footer">
            <span class="pull-left dialog-extra-options">
                <yield from="options"/>
            </span>
            <button class="btn btn-primary" data-dismiss="modal" aria-hidden="true">Close</button>
        </div>
    </div>

    <script>
        this.title = this.opts.title;

        /*
         * Show the modal dialog.
         */
        showDialog(){
            $('.modal', this.root).modal();
        }
    </script>
</modaldialog>
