<aboutdialog>
    <modaldialog title="About TextCritical.net" versioninfo={ versioninfo }>
        <yield to="body">
            TextCritical.net is a website that provides ancient Greek texts and useful analysis tools.
            <div class="section-splitter"/>
            This website was created by <a href="mailto:Luke@TextCritical.net">Luke Murphey</a>.
            <div class="section-splitter"/>
            <table class="version-info">
                <tbody>
                    <tr>
                        <td><strong>Version</strong></td>
                        <td>{ opts.versioninfo }</td>
                    </tr>
                    <tr>
                        <td><strong>Source Code</strong></td>
                        <td>Available at <a target="_blank" class="external print-append-href" href="https://github.com/LukeMurphey/textcritical_net">Github.com</a></td>
                    </tr>
                    <tr>
                        <td><strong>Licenses</strong></td>
                        <td>Available at <a target="_blank" class="external print-append-href" href="https://lukemurphey.net/projects/ancient-text-reader/wiki/Dependencies">LukeMurphey.net</a></td>
                    </tr>
                </tbody>
            </table>
        </yield>
        <yield to="options">
            <a target="_blank" href="contact">Contact Us</a>
        </yield>
    </modaldialog>
    <style>
        table.version-info{
            margin: 0px 8px 0px 0px;
        }

        table.version-info td{
            padding-right: 16px;
            padding-bottom: 6px;
        }

        .section-splitter{
            margin-top: 12px;
        }
    </style>
    <script>
        this.versioninfo = this.opts.version_info;

        //riot.mount('modaldialog');

    	// Run the functions as necessary on mount.
        this.on('mount', function(){
            // Listen for the event to open the modal
            if(this.opts.observable){
                this.opts.observable.on('open-about-modal', function() {
                    this.tags.modaldialog.showDialog();
                }.bind(this));
            }
            else{
                console.warn('Observable was empty; will not be able to monitor for the calls to open the about dialog');
            }
        }.bind(this))

        
    </script>

</aboutdialog>