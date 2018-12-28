<dialog>
    <div class="dialog_header">
        <div class="dialog_header_text">This is a test</div>
        <button type="button" class="close" aria-hidden="true">×</button>
    </div>
    <div>
    </div>
    <style>
        .dialog_header_text {
            margin-top: 6px;
            display: inline-block;
        }

        .dialog_header {
            border-bottom: 1px solid #222222;
            height: 32px;
            padding: 4px;
        }

        .dialog_header > button {
            margin-right: 8px;
        }

        dialog {
            position: fixed;
            width: 100%;
            bottom: 0;
            height: 320px;
            display: block;
            border: 0;
            background-color: #373737; /* #363636; */
            color: white;
            padding: 0;
            z-index: 1;
        }
    </style>
    <script>
        this.title = this.opts.title;
        this.content = this.opts.content;

        /*
         * Show the dialog.
         */
        showDialog(){
            
        }
    </script>
</dialog>
