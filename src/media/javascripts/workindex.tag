<workindex>
        <table class={table: true, "table-striped": display_full_table, "table-hover": true, "fulltable": display_full_table} class="table table-striped table-hover" id="works_list" >
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
                        <div class="pull-left work-icon-holder">
							<a href="{ read_work_url }/{ title_slug }">
                            <img class="work-image" src="/work_image/{ title_slug }?width=30">
							</a>
                        </div>
                        <div class="work-description" >
                            <div><a href="{ read_work_url }/{ title_slug }">{ title }</a></div>
                            <div>in { language }<span if={ author }> by { author }</span><span if="{ editor }"> (edited by { editor })</span></div>
                        </div>
                    </td>
			        <td class="hidden-phone">
						<div class="dropdown work-options">
							<a class="dropdown-toggle" type="button" data-toggle="dropdown">Options<span class="caret"></span></a>
							<ul class="dropdown-menu">
								<li><a href="{ search_url }?q=work:{ title_slug }">Search</a></li>
								<li><a href="#" class="open-work-info" data-work-title-slug="{ title_slug }" data-work-title="{ title }">Info</a></li>
							</ul>
						</div>
                    </td>
			    </tr>
		    </tbody>
		    <tbody if={ display_full_table }>
			    <tr each={ works }>
					<!--
			        <td><i class="hidden-phone icon-book icon-white"></i> <a href="{ read_work_url }/{ title_slug }">{ title }</a> </td>
					-->
					<td><img class="work-image " src="/work_image/{ title_slug }?width=30"> <a href="{ read_work_url }/{ title_slug }">{ title }</a> </td>
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
		<div class="loading-holder">
			<yield/>
		</div>
<style>
	.fulltable .work-image{
		width:24px;
		height:32px
	}
</style>
<script>
    // Initialize the arguments
    this.use_dark_theme = true; //this.opts.usedarktheme === undefined ? true : false;
    this.read_work_url = this.opts.readworkurl;
    this.search_url = this.opts.searchurl;
    this.filter = this.opts.filter;
    this.display_full_table = this.opts.displayfulltable === undefined ? false : true;
    this.page_length = this.opts.page_length === undefined ? 10 : parseInt(this.opts.page_length, 10);
	this.wait_to_render = this.opts.wait_to_render === undefined ? false : true;

	// This is an internal parameter for storing the works
    this.works = [];
	this.datatable = null;

	// Run the functions as necessary on mount.
	this.on('mount', function(){
		if(!this.wait_to_render){
			this.getWorks();
		}
	}.bind(this))

	updateFilter(){
		this.datatable.fnFilter($('input.works-search-query').val());
	}
	
	updateMainFilter(){
		$('input.works-search-query').val($('input[aria-controls="works_list"]').val());
	}
	
	setupWorksTable(works){
		this.works = works;
        this.update();

    	this.datatable = $('#works_list').dataTable( {
            "bPaginate": true,
            "bLengthChange": false,
            "bJQueryUI": false,
            "bFilter": true,
            "bSort": true,
            "bInfo": true,
            "bAutoWidth": false,
            "pageLength": this.page_length,
			"aoColumns": [
				null,                   // Title
				{ "bSortable": false }  // Actions
			]
		} );
		
        // Filter the table if requested
		if(this.filter){
            this.datatable.fnFilter(this.filter);
        }

        // Wire up the controls
		$('input.works-search-query').keyup(_.debounce(this.updateFilter, 150));
		$('input.works-search-query').change(_.debounce(this.updateFilter, 150));
		$('#search').submit( function() { return false; });
		
		$('input[aria-controls="works_list"]').keyup(_.debounce(this.updateMainFilter, 150));
		
		$('#async-loading-message').hide();
		$('#works_list', this.root).fadeIn('slow');
	}

    getWorks(){
		var promise = jQuery.Deferred();

        $.ajax({
    		url: "/api/works"
    	}).done(function(works) {
    		this.setupWorksTable(works);
			$('.loading-holder', this.root).hide();
			promise.resolve();
    	}.bind(this));

		return promise;
    }

</script>
</workindex>