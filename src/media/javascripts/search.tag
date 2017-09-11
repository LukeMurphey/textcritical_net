<search>
<form id="search-form" onsubmit={ search }>
	<legend>Search</legend>
	
	<div class="input-append ">

	 	<input class="span10" ref="searchterm" autocorrect="off" autocapitalize="off" placeholder="Enter the text to search for (e.g. νόμου or no/mou)" type="text" value="{query}"/>
	 	<input type="hidden" ref="pagenumber" name="page" value="{page}" />
	 	
	 	<button id="search-button" class="btn btn-primary" type="button" onclick={ search }><span class="hidden-phone">Submit </span>Search</button>
	</div>
	<label class="checkbox inline no-left-padding" for="related_forms">
		<input class="checkbox" type="checkbox" ref="relatedforms" id="related_forms" name="related_forms" checked={ search_related_forms }>Search related Greek forms<span class="hidden-phone"> (slower but more thorough)</span></input>
	</label>
	<label class="checkbox inline" for="ignore_diacritics">
		<input class="checkbox" type="checkbox" ref="ignorediacritics" id="ignore_diacritics" name="ignore_diacritics" checked={ ignore_diacritics }>Search ignoring diacritics</input>
	</label>
</form>

<div class="tabbable">
  <ul class="nav nav-tabs">
    <li class="active">
    	<a href="#search-results-tab" data-toggle="tab">Results</a>
    </li>
    <li>
    	<a href="#search-stats-tab" data-toggle="tab">Matched words</a>
    </li>
    <li>
    	<a href="#search-stats-tab1" data-toggle="tab">Matched works</a>
    </li>
    <li>
    	<a href="#search-stats-tab2" data-toggle="tab">Matched sections</a>
    </li>
    <li>
    	<a href="#search-help-tab" data-toggle="tab">Help</a>
    </li>
  </ul>
   
  <div class="tab-content">
    <div class="tab-pane active" id="search-results-tab">
		<div class="search-results" id="search-results-content">

			<span if={ search_error }>
				<h4>Search failed</h4> The search request could not be completed
			</span>

			<div if={ !search_error && search_results && search_results.results && search_results.results.length == 0 } class="alert alert-block">
				No results were found matching the provided search
			</div>
		
			<span each={ !search_error && search_results && search_results.results }>
				<div class="work-description">
					<a href="{ url }{ highlight_url }">{ work }, { description }</a>
				</div>
				<div if={ highlights.length > 0 } class="highlights">
					<raw content="{ highlights }" />
				</div>
				<div if={ highlights.length <= 0 } class="highlights">
					<raw content="{ content_snippet }" />
				</div>
			</span>
		</div>
	<div if={ !search_error && search_results && search_results.result_count > 0 } class="search-results-page-info">{ result_text }</div>

	<ul class="pager">
		<li class={ disabled: !has_previous, previous: true }>
			<a class="previous-page-link" onclick={ searchPreviousPage }>&larr; Previous</a>
		</li>
		<li class={ disabled: !has_next, next: true }>
			<a class="next-page-link" onclick={ searchNextPage }>Next &rarr;</a>
		</li>
	</ul>

  </div>
    <div class="tab-pane" id="search-stats-tab">
    	<div class="chart" id="chart-word-frequency"></div>
    	<!-- <div class="chart" id="chart-work-frequency"></div>
    	<div class="chart" id="chart-section-frequency"></div> -->
    </div>
    <div class="tab-pane" id="search-stats-tab1">
    	<div class="chart" id="chart-work-frequency"></div>
    </div>
    <div class="tab-pane" id="search-stats-tab2">
    	<div class="chart" id="chart-section-frequency"></div>
    </div>
    <div class="tab-pane" id="search-help-tab">
		<div id="search-help">
			
			<h3>Search Operations</h3>
			
			<p>
			The search language used by TextCritical.net allows several operations. Here are some common ones:
			</p>
			
			<p>
			Search for verses with both ἱστορίας and νόμον:
			<div class="search-example">ἱστορίας νόμον</div>
			</p>
			
			<p>
			Search for verses with the phrase "ἱστορίας νόμον":
			
			<div class="search-example">"ἱστορίας νόμον"</div>
			</p>
			
			<p>
			Search for verses with the word ἱστορίας or νόμον:
			<div class="search-example">ἱστορίας OR νόμον</div>
			</p>
			
			
			<p>
			Search for verses with the word συγγνώμην provided they don't include either ἱστορίας or νόμον:
			<div class="search-example">συγγνώμην NOT (ἱστορίας OR νόμον)</div>
			</p>
			
			
			<p>
			The search engine accepts <a target="_blank" class="external" href="http://en.wikipedia.org/wiki/Beta_code">beta-code</a> representations of Greek words. Thus, a search for no/mon is equivalent to a search for νόμον:
			<div class="search-example">no/mon</div>
			</p>
			
			<p>
			<span class="label label-info">Heads up!</span> If you are searching using beta-code, make sure to put your search query in single quotes (e.g. 'no/mon')
			</p>
			
			<h3>Searching Related Forms</h3>
			<p>
			Searching for related forms causes the search engine to look for all other variations of a word. For example, a search for ἀδελφός would also search for ἀδελφοί, ἀδελφοῦ, ἀδελφοί, etc.
			</p>
			<p>
			<span class="label label-info">Heads up!</span> Searching for related forms is considerably slower than searching for a particular form.
			</p>
			
			<h3>Search Fields</h3>
			
			Several fields exist that can be be searched. Just append the field name to the search with a colon to search it (e.g. work:new-testament).
			
			Below are the available fields
			<p>
				<table class="table table-bordered">
					<thead>
						<tr>
							<th>Field</th>
							<th>Description</th>
							<th>Example</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td>work</td>
							<td>Search for items within a particular work (New Testament, Agammenon, etc.)</td>
							<td><span class="search-example"><span class="search-example">work:"New Testament"</span></td>
						</tr>
						<tr>
							<td>no_diacritics</td>
							<td>Search for words disregarding the diacritical marks. Searching for no_diacritics:και will match on καὶ and καῖ</td>
							<td><span class="search-example">no_diacritics:ευαγγελιον</span></td>
						</tr>
						<tr>
							<td>section</td>
							<td>Search for items within a section (chapter, division, book, etc.)</td>
							<td><span class="search-example">section:"Matthew 5"</span></td>
						</tr>
						<tr>
							<td>author</td>
							<td>Search for verses within works created by a particular author.</td>
							<td><span class="search-example">author:"Flavius Josephus"</span></td>
						</tr>
					</tbody>
				</table>
			</p>
		</div>
    </div>
  </div>
</div>

<div id="searching" class="hide hidden-phone searching-animation">Searching ...</div>
    <script>
		// Initialize the arguments
		this.update_url = this.opts.updateurl === undefined ? false : true;
		this.run_automatically = this.opts.runautomatically === undefined ? false : true;
        this.page = parseInt(this.opts.page === undefined ? 1 : this.opts.page, 10);
        this.query = this.opts.query;
		this.ignore_diacritics = this.opts.ignorediacritics === undefined ? false : true;
		this.search_related_forms = this.opts.searchrelated === undefined ? false : true;

		// Initialize the parameters for how the search executes
		this.highlight_url = "";
		this.has_next = false;
		this.has_previous = false;

		this.search_results = null;
		this.search_error = false;

		// Run the functions as necessary on mount.
		this.on('mount', function(){
			this.runSearchAutomaticallyIfNecessary();

			// Wire up the event listener for the back button press
			if(this.update_url){
				window.addEventListener('popstate', this.searchPagePopstate.bind(this));
			}
			
		}.bind(this))

		/*
		 * Run the search automatically if requested and a query was provided.
		 */
		runSearchAutomaticallyIfNecessary(){
			// Execute the search automatically if we already have a search term
			if(this.run_automatically && this.refs.searchterm.value.length > 0 && this.containsSearchWords(this.refs.searchterm.value)){
				this.search(null, true);
			}
			
			// Set the caret at the end of the search term
			this.setCaretAtEnd(this.refs.searchterm);
		}

		/*
		 * Update the URL according to the search form.
		 */
		setURL(){
			var params = {};
			
			// Add the related forms argument
			if(this.refs.relatedforms.checked){
				params['include_related'] = 1;
			}
			
			// Add the ignore diacritics argument
			if(this.refs.ignorediacritics.checked){
				params['ignore_diacritics'] = 1;
			}

			// Get the appropriate URL
			if(this.page <= 1 || parseInt(this.page) <= 1){
				params['q'] = this.refs.searchterm.value;
				page = 1;
			}
			else{
				params['q'] = this.refs.searchterm.value;
				params['page'] = this.page;
			}

			// Make the URL
			var url = document.location.pathname + "?" + $.param(params); // jQuery

			// Push the state
			history.pushState(
				{
					query: this.refs.searchterm.value,
					page: this.page,
					include_related_forms: this.refs.relatedforms.checked,
					ignore_diacritics: this.refs.ignorediacritics.checked
				},
				document.title,
				url
			);
		}

		/*
		 * Update the results based on the given results.
         */
		updateResults(search_results){
			// Store the results
			this.search_results = search_results;

			// Set the highlight URL
			this.highlight_url = "";
			
			for (term in search_results.matched_terms){
				if(this.highlight_url == ""){
					this.highlight_url = "?";
				}
				
				this.highlight_url += ("&highlight=" + term);
			}

			// Determine if we have next results
			if(search_results.result_count > (search_results.page * search_results.page_len)){
				this.has_next = true;
			}
			else{
				this.has_next = false;
			}

			// Determine if we have previous results
			if(search_results.page <= 1){
				this.has_previous = false;
			}
			else{
				this.has_previous = true;
			}

			// Create the text describing the results
			this.result_text = "";

			if(search_results.result_count > 0){
				this.result_text = 'Page ' + search_results.page + ' of ' + Math.ceil(search_results.result_count / search_results.page_len);
			}

			if(search_results.match_count > 0){
				this.result_text = this.result_text + ' (' + search_results.match_count + ' word matches in ' + search_results.result_count + ' verses)';
			}
			else{
				this.result_text = this.result_text + ' (' + search_results.result_count + ' verses)';
			}

			// Force the UI to refresh
			this.update();

			// Make bar charts of the word, work and section frequency
			TextCritical.make_bar_chart( $('#chart-word-frequency'), 'Frequency of matched words', search_results.matched_terms, "No data available on matched terms" );
			TextCritical.make_bar_chart( $('#chart-work-frequency'), 'Number of matched verses by work', search_results.matched_works, "No data available on matched works" );
			TextCritical.make_bar_chart( $('#chart-section-frequency'), 'Number of matched verses by section', search_results.matched_sections, "No data available on matched sections" );
		}

		/*
		 * Show an indicator that the search is progressing.
		 */
		showSearchProgress(){
			$('#searching').show();
			$('#search-results-content').block({ message: null, overlayCSS: { backgroundColor: '#2f2f2f', opacity: 0.8 } }); 
		}

		/*
		 * Hide the indicator that the search is progressing.
		 */
		hideSearchProgress(){
			$('#searching').hide();
			$('#search-results-content').unblock();
			$('#search-results-content').show();
		}

		/**
		 * Determine if the results has actual words to kick off a search to look for (other than just the parts of the search specifying
		 * the work to search).
		 **/
		containsSearchWords(query) {
			if(!query){
				return false;
			}

			var split_query = query.match(/([_0-9a-z]+[:][-_0-9a-z]+)|([\w_]+[:]["][-\w ]*["])|([^ :]+)/gi);
			
			if(split_query === null){
				return false;
			}

			for(c = 0; c < split_query.length; c++){
				if( split_query[c].search(":") < 0 ){
					return true;
				}
			}
			
			return false;
		}

		/*
		 * Set the cursor to the end of the element.
		 */
		setCaretAtEnd(elem) {
		    var elemLen = elem.value.length;
		    
		    // For IE Only
		    if (document.selection) {
		        // Set focus
		        elem.focus();
		        // Use IE Ranges
		        var oSel = document.selection.createRange();
		        // Reset position to 0 & then set at end
		        oSel.moveStart('character', -elemLen);
		        oSel.moveStart('character', elemLen);
		        oSel.moveEnd('character', 0);
		        oSel.select();
		    }
		    else if (elem.selectionStart || elem.selectionStart == '0') {
		        // Firefox/Chrome
		        elem.selectionStart = elemLen;
		        elem.selectionEnd = elemLen;
		        elem.focus();
		    }
		}

		/*
		 * Search when the user hits back by popping the state from the history.
		 */
		searchPagePopstate(e){

			// Ignore events made from replace states
			if (e.state == null) {
				return;
			}
			  
			// Update the query if necessary
			this.refs.searchterm.value = e.state.query;
			
			// Invoke the search, but don't update the URL (otherwise users will keep adding a new state and can never get back more than one)
			if(e.state.page){
				this.page = e.state.page;
			}
			else{
				this.page = 1;
			}
			
			this.search(e, true);
		}

		/*
		 * Do a search against the next page of results.
		 */
		searchNextPage(e){
			if(this.has_next){
				this.page += 1;

				this.search(e);
			}
		}

		/*
		 * Do a search against the previous page of results.
		 */
		searchPreviousPage(e){
			if(this.page <= 1){
				this.page = 1;
			}
			else{
				this.page -= 1;
			}

			this.search(e);
		}

		/**
		 * Perform a search.
		 **/
		search(e, skip_updating_url){

			// Assign a default to dont_update_url
			if(typeof skip_updating_url === 'undefined'){
				var skip_updating_url = false;
			}

			// Update the URL if requested
			if(this.update_url && !skip_updating_url){
				this.setURL();
			}

			// Get the parameters to perform the search
			var searchterm = this.refs.searchterm.value;
			var related_forms = this.refs.relatedforms.checked ? 1 : 0;
			var ignore_diacritics = this.refs.ignorediacritics.checked ? 1 : 0;

			// Assign a value to the page number if it is not valid
			if( this.page <= 0 ){
				console.warn("Page number is invalid (must be greater than zero)");
				this.page = 1;
			}

			// Show the searching window
			this.showSearchProgress();

			console.info("Executing search on page " + this.page + " for " + searchterm);

			// Submit the AJAX request to display the information
			$.ajax({
				url: "/api/search/" + encodeURIComponent(searchterm) + "?page=" + this.page + "&related_forms=" + related_forms + "&ignore_diacritics=" + ignore_diacritics
			})
			.done(function(search_results) {
				this.updateResults(search_results);
				this.hideSearchProgress();
				this.search_error = false;
			}.bind(this))
			.error(function(jqXHR, textStatus, errorThrown) {
				console.error("The request to search failed for " + searchterm);
				this.search_error = true;
				this.update();
				this.hideSearchProgress();
			}.bind(this));

			e.preventDefault();
		}
    </script>
</search>