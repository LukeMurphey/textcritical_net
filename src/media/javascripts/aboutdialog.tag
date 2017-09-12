<aboutdialog>
    <modaldialog title="About TextCritical.net">
        <yield to="body">
            TextCritical.net is a website that provides ancient Greek texts and useful analysis tools.
            <a target="_blank" class="external print-append-href" href="https://lukemurphey.net/projects/ancient-text-reader/">LukeMurphey.net</a>
            <table>
                <tbody>
                    <tr>
                        <td><strong>Version</strong></td>
                        <td>1.7</td>
                    </tr>
                    <tr>
                        <td><strong>Source Code</strong></td>
                        <td>Available at <a target="_blank" class="external print-append-href" href="https://github.com/LukeMurphey/textcritical_net">Github.com</a></td>
                    </tr>
                    <tr>
                        <td><strong>Dependencies</strong></td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        </yield>
        <yield to="options">
            <a target="_blank" href="contact">Contact Us</a>
        </yield>
    </modaldialog>
    <script>
        riot.mount('modaldialog');

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