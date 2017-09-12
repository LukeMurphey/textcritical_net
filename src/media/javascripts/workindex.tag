<workindex>
        <table class={table: true, "table-striped": display_full_table, "table-hover": true} class="table table-striped table-hover" id="works_list" >
		    <thead if={ !display_full_table }>
		        <th>Title</th>
		        <th></th>
		    </thead>
		    <thead if={ display_full_table }>
		        <th>Title</th>
		        <th>Language</th>
		        <th>Author</th>
		        <th class="hidden-phone">Editor</th>
		        <th></th>
		    </thead>
		    <tbody if={ !display_full_table }>
			    <tr each={ works }>
			        <td>
                        <div class="pull-left" style='width:42px;height:40px;'>
                            <img class="work-image" src="/work_image/{ title_slug }?width=30">
                        </div>
                        <div>
                            <div><a href="{ read_work_url }/{ title_slug }">{ title }</a></div>
                            <div>in { language } by { author } <span if="{ editor }">(edited by { editor })</span></div>
                        </div>
                    </td>
			        <td class="hidden-phone">
                        <a href="{ search_url }?q=work:{ title_slug }">[Search]</a>
                        <a href="#" class="open-work-info" data-work-title-slug="{ title_slug }" data-work-title="{ title }">[Info]</a>
                    </td>
			    </tr>
		    </tbody>
		    <tbody if={ display_full_table }>
			    <tr each={ works }>
			        <td><i class="hidden-phone icon-book icon-white"></i> <a href="{ read_work_url }/{ title_slug }">{ title }</a> </td>
			        <td>{ language }</td>
			        <td>{ author }</td>
			        <td class="hidden-phone">{ editor }</td>
			        <td class="hidden-phone">
                        <a href="{ search_url }?q=work:{ title_slug }">[Search]</a>
                        <a href="#" class="open-work-info" data-work-title-slug="{ title_slug }" data-work-title="{ title }">[Info]</a>
                    </td>
			    </tr>
		    </tbody>
		</table>
<script>
    // Initialize the arguments
    this.use_dark_theme = true; //this.opts.usedarktheme === undefined ? true : false;
    this.read_work_url = this.opts.readworkurl;
    this.search_url = this.opts.searchurl;
    this.filter = this.opts.filter;
    this.display_full_table = this.opts.displayfulltable === undefined ? false : true;
    this.page_length = this.opts.page_length === undefined ? 10 : this.opts.page_length;
    this.works = [];

	// Run the functions as necessary on mount.
	this.on('mount', function(){
		this.getWorks();
	}.bind(this))

	updateFilter(){
		textcritical.datatable.fnFilter($('input.works-search-query').val());
	}
	
	updateMainFilter(){
		$('input.works-search-query').val($('input[aria-controls="works_list"]').val());
	}
	
	setupWorksTable(works){
		this.works = works;
        this.update();

    	textcritical.datatable = $('#works_list').dataTable( {
            "bPaginate": true,
            "bLengthChange": false,
            "bJQueryUI": false,
            "bFilter": true,
            "bSort": true,
            "bInfo": true,
            "bAutoWidth": false,
            "pageLength": this.page_length
		} );
		
        // Filter the table if requested
		if(this.filter){
            textcritical.datatable.fnFilter(this.filter);
        }

        // Wire up the controls
		$('input.works-search-query').keyup(_.debounce(this.updateFilter, 150));
		$('input.works-search-query').change(_.debounce(this.updateFilter, 150));
		$('#search').submit( function() { return false; });
		
		$('input[aria-controls="works_list"]').keyup(_.debounce(this.updateMainFilter, 150));
		
		$('#async-loading-message').hide();
		$('#works_list').fadeIn('slow');
	}

    getWorks(){
        $.ajax({
    		url: "/api/works"
    	}).done(function(works) {
    		this.setupWorksTable(works);
    	}.bind(this));
    }

</script>
</workindex>