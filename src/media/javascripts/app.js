/* Author: Luke Murphey

*/

var TextCritical = {};

define([
        'jquery',
        'underscore',
        'highcharts',
        'libs/text!/media/templates/alert_message.html',
        'libs/text!/media/templates/morphology_dialog.html',
        'libs/text!/media/templates/work_info_dialog.html',
        'libs/text!/media/templates/loading_dialog.html',
        'libs/text!/media/templates/search_results.html',
        'libs/optional!facebook'
    ],
    function($, _, highcharts, alert_message_template, morphology_dialog_template, work_info_dialog_template, loading_template, search_results_template) {
	
		/**
		 * Causes the verses to break onto separate lines. 
		 **/
		TextCritical.setFormatBreakLine = function () {
			$('.verse-container').addClass("block");
			$('.align-break').addClass('active');
		}
		
		/**
		 * Causes the verses to not break onto separate lines. 
		 **/
		TextCritical.unSetFormatBreakLine = function () {
			$('.verse-container').removeClass("block");
			$('.align-break').removeClass('active');
		}
		
		/**
		 * Toggles the table-of-contents.
		 **/
		TextCritical.toggleTOC = function (){
			
			if( $('.table-of-contents').is(":visible") ){
				$('#show-table-of-contents-phone').text("Show table of contents");
			}
			else{
				$('#show-table-of-contents-phone').text("Hide table of contents");
			}
			
			$('.table-of-contents').toggle('fast', function() {
				// Clear the division filter
				$(".division-filter").val("");
				$(".division-filter").change();
			});
			
		}
		
		/**
		 * Toggles the verse breaks.
		 **/
		TextCritical.toggleVerseBreak = function (){
			break_verses = !break_verses;
			
			if( break_verses ){
				TextCritical.setFormatBreakLine();
			}
			else{
				TextCritical.unSetFormatBreakLine();
			}
			
			settings.set("break_verses", break_verses);
		}
		
		/**
		 * Escape the identifier so that if it contains periods, it can still be used as a jQuery selector.
		 * 
		 * @param id The identifier to escape
		 **/
		TextCritical.escapeIdentifier = function (id) {
			return id.replace(".", "\\.");
		}
		
		/**
		 * Scrolls to the given anchor.
		 * @param id The id to scroll to
		 **/
		TextCritical.scrolltoAnchor = function (id) {
			
			scrollTo = $("#"+ id ).offset();
			
			if( typeof scrollTo == "undefined" ){
				console.warn("The id (" + id + ") to scroll to is undefined");
			}
			else{
				$('html,body').animate({scrollTop: scrollTo.top},'slow');
			}
		}
		
		/**
		 * Highlight a selected verse without performing a request to the server.
		 * 
		 * @param verse_number The verse number that we are selecting
		 * @param base_chapter_url The URL of the current chapter
		 **/
		TextCritical.scrollToVerse = function (verse_number, base_chapter_url) {
		
			// Make sure a base chapter URL was provided
			if ( typeof base_chapter_url == "undefined" || base_chapter_url == null ){
				console.warn("No base chapter URL was provided; will not be able to update the URL for the given verse");
				return true; // Let the href propagate
			}
			
			// The ID of the verse number element
			var id = "verse-" + verse_number;
			var escapted_id = TextCritical.escapeIdentifier(id);
			
			// Update the URL
			title = document.title;
			history.pushState( {verse: verse_number}, title, base_chapter_url + "/" + verse_number + document.location.search);
			console.info("Updating the URL to point to the selected verse");
			
			// Remove existing highlights
			$('.verse-container').removeClass('highlighted');
			$('.verse.number').removeClass('label-info');
			
			// Highlight the new verse
			$('#' + escapted_id).addClass('highlighted');
			$('#' + escapted_id + ' .label').addClass('label-info');
			
			// Scroll to the verse
			TextCritical.scrolltoAnchor(escapted_id);
			
			return false; // Stop the page from reloading
			
		}
		
		/**
		 * Loads the client-saved settings.
		 **/
		TextCritical.loadStoreSettings = function () {
			
			var defaults = {
				"break_verses": false
			};
			
			settings = new Store("settings");
			
			break_verses = settings.get("break_verses", defaults);
			
			if( break_verses ){
				TextCritical.setFormatBreakLine();
			}
		}
		
		/**
		 * Slugifies some text.
		 * 
		 * @param text The text to slugify.
		 **/
		TextCritical.slugify = function (text) {
			text = text.replace(/[^-a-zA-Z0-9,&\s]+/ig, '');
			text = text.replace(/-/gi, "_");
			text = text.replace(/\s/gi, "-");
			return text;
		}
		
		/**
		 * Opens the view to the given chapter reference.
		 * 
		 * @param reference the reference to go to (like "Romans 14:1")
		 * @param work_title_slug the title slug of the work containing the referenced item
		 **/
		TextCritical.go_to_chapter = function ( reference, work_title_slug ) {
			document.location = TextCritical.resolve_path(work_title_slug, reference);
		}
		
		/**
		 * Opens the morphology dialog on the word within the text clicked.
		 **/
		TextCritical.word_lookup = function () {
			
			// Get the work information
			var work = $("h1[data-work-title-slug]").data("work-title-slug");
			
			// Get the current division name
			var division_data = $('#chapter-base-url').data();
			
			if(division_data && division_data.chapterDescription){
				TextCritical.open_morphology_dialog( $(this).text(), work, division_data.chapterDescription );
			}
			else{
				TextCritical.open_morphology_dialog( $(this).text(), work );
			}
			
			return false;
		}
		
		/**
		 * Opens a dialog that obtains the morphology of a word.
		 * 
		 * @param title the title of the dialog
		 * @param content the content for the dialog
		 * @param extra_options the content for the extra options section
		 **/
		TextCritical.open_dialog = function ( title, content, extra_options ) {
			
			if ( typeof extra_options == "undefined" || extra_options == null ){
				extra_options = '';
			}
			
			// Reset the content to the loading content
			$("#popup-dialog-content").html(content);
			
			// Set the link to Google
			var extra_options_template = 'Look up at <a target="_blank" href="http://www.perseus.tufts.edu/hopper/morph?l=<%= word %>&la=greek">Perseus</a> or <a target="_blank" href="https://www.google.com/search?q=<%= word %>">Google</a>';
			
			$("#popup-dialog-extra-options").html(extra_options);
			
			// Set the title
			$("#popup-dialog-label").text(title);
			
			// Open the form
			$("#popup-dialog").modal();
			
		}
		
		/**
		 * Opens a dialog that obtains the morphology of a word.
		 * 
		 * @param word the word to look up
		 * @param work the work that contains the word we are looking up
		 **/
		TextCritical.open_morphology_dialog = function ( word, work, division ) {
		
			if(typeof division === "undefined"){
				var division = null;
			}
			
			console.info( "Obtaining the morphology of " + word );
		
			// Trim the word in case extra space was included
			word = TextCritical.trim(word);
		
			// Reset the content to the loading content
			$("#popup-dialog-content").html(_.template(loading_template,{ message: "Looking up morphology for " +  _.escape(word) + "..." }));
		
			// Set the link to Google
			var extra_options_template = 'Look up at <a target="_blank" href="http://www.perseus.tufts.edu/hopper/morph?l=<%= word %>&la=greek">Perseus</a> or <a target="_blank" href="https://www.google.com/search?q=<%= word %>">Google</a>';
		
			$("#popup-dialog-extra-options").html(_.template(extra_options_template,{ word : word }));
		
			// Set the title
			$("#popup-dialog-label").text("Morphology: " +  _.escape(word) );
		
			// Open the form
			$("#popup-dialog").modal();
		
			// Submit the AJAX request to display the information
			$.ajax({
				url: "/api/word_parse/" + word
			}).done(function(data) {
		
				// Render the lemma information
				$("#popup-dialog-content").html(_.template(morphology_dialog_template,{parses:data, word: _.escape(word), work: work, division: _.escape(division)}));
		
				// Set the lemmas to be links
				$("a.lemma").click(TextCritical.word_lookup);
		
				console.info( "Successfully performed a request for the morphology of " + word );
		
			}).error( function(jqXHR, textStatus, errorThrown) {
				$("#popup-dialog-content").html( "<h4>Parse failed</h4> The request to parse could not be completed" );
				console.error( "The request for the morphology failed for " + word );
			});
		}
		
		/**
		 * Opens a dialog that shows the information about a topic.
		 * 
		 * @param topic the topic (author or work) to get information for
		 **/
		TextCritical.open_topic_dialog = function ( topic, search, topic_type ) {
			
			if(typeof topic_type === "undefined"){
				var topic_type = null;
			}
			
			if(typeof search === "undefined"){
				var search = topic;
			}
			
			console.info( "Obtaining information about " + topic );
		
			// Trim the topic in case extra space was included
			search = TextCritical.trim(search);
		
			// Reset the content to the loading content
			$("#popup-dialog-content").html(_.template(loading_template,{ message: "Looking up info for " +  _.escape(topic) + "..." }));
		
			$("#popup-dialog-extra-options").html("");
			
			// Set the title
			$("#popup-dialog-label").text( _.escape(topic) );
		
			// Open the form
			$("#popup-dialog").modal();
		
			// Submit the AJAX request to display the information
			$.ajax({
				url: "/api/wikipedia_info/" + search
			}).done(function(data) {
				
				data['topic'] = topic;
				
				// Set the link to Wikipedia
				var extra_options_template = '<a target="_blank" class="external" href="<%= url %>">View on wikipedia</a>';
			
				$("#popup-dialog-extra-options").html(_.template(extra_options_template,{ url : data.url }));
				
				// Render the lemma information
				$("#popup-dialog-content").html(_.template(work_info_dialog_template, data));
		
				console.info( "Successfully performed a request for information on " + topic );
		
			}).error( function(jqXHR, textStatus, errorThrown) {
				
				// Handle cases where the request succeeded but no information could be found
				if(jqXHR.status === 403){
					$("#popup-dialog-content").html( "<h4>No information</h4>No information could be found for " +  _.escape(topic) + "." );
					console.warn( "No information could be obtained for " + topic );
				}
				
				// Handle errors
				else{
					$("#popup-dialog-content").html( "<h4>Request failed</h4> The request for information could not be completed" );
					console.error( "The request on the topic failed for " + topic );
				}
			});
		}
		
		/**
		 * Trims the string.
		 * 
		 * @param s the string to be stripped
		 */
		TextCritical.trim = function (s) {
		    return String(s).replace(/^\s+|\s+$/g, '');
		}
		
		/**
		 * Shorten a string.
		 * 
		 * @param s the string to be stripped
		 * @param n the desired length
		 * @param use_word_boundary if true, then the string will be shortened while attempting to avoid a break in a word
		 * @param shorten_text the text to add if the string is shortened
		 */
		TextCritical.shorten = function(s, n, use_word_boundary, shorten_text){
			
			if( typeof shorten_text == "undefined" || shorten_text == null ){
				var shorten_text = '&hellip;'; // An ellipsis
			}
			
			if( typeof use_word_boundary == "undefined" || use_word_boundary == null ){
				var use_word_boundary = true;
			}
			
		    var toLong = s.length > n,
		    s_ = toLong ? s.substr(0,n-1) : s;
		    s_ = use_word_boundary && toLong ? s_.substr(0,s_.lastIndexOf(' ')) : s_;
		    return  toLong ? s_ + shorten_text : s_;
			
		}
		
		/**
		 * Highlights the word that the user is focusing on or hovering over.
		 **/
		TextCritical.highlight_selected_word = function () {
			TextCritical.highlight_word( $(this).text() );
		}
		
		/**
		 * Unhighlights all words.
		 */
		TextCritical.unhighlight_all_words = function (div_class) {
			
			if(typeof div_class == 'undefined'){
				var div_class = 'highlighted';
			}
			
			$('.word').removeClass(div_class);
		}
		
		/**
		 * Highlights all of the word nodes with the given text.
		 * 
		 * @param word The word to highlight
		 */
		TextCritical.highlight_word = function ( word, div_class, remove_existing_highlights ) {
			
			if(typeof div_class == 'undefined'){
				var div_class = 'highlighted';
			}
			
			if(typeof remove_existing_highlights == 'undefined'){
				var remove_existing_highlights = true;
			}
			
			// Unhighlight all existing words to make sure we don't accumulate highlights
			if(remove_existing_highlights){
				TextCritical.unhighlight_all_words(div_class);
			}
			
			// Make the regular expression for finding the words
			var escaped_word = TextCritical.escape_regex(word.normalize());
			var pattern = new RegExp("^" + escaped_word + "$", "i");
			console.info( "Highlighting " + word );
			
			// Add the CSS to make these words highlighted
			$('.word').filter(function(){
		  		return pattern.test($(this).text().normalize())
			}).addClass(div_class);
		}
		
		/**
		 * Determine if the results has actual words to kick off a search to look for (other than just the parts of the search specifying
		 * the work to search).
		 * 
		 * @param query The query to perform a search on
		 **/
		TextCritical.contains_search_words = function ( query ) {
			
			var split_query = query.match(/([_0-9a-z]+[:][-_0-9a-z]+)|([\w_]+[:]["][-\w ]*["])|([^ :]+)/gi);
			
			for( c = 0; c < split_query.length; c++){
				if( split_query[c].search(":") < 0 ){
					return true;
				}
			}
			
			return false;
		}
		
		/**
		 * Set the cursor to the end of an input.
		 * 
		 * @param elem Set the cursor at the end of the given element
		 **/
		TextCritical.set_caret_at_end = function (elem) {
			
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
		
		/**
		 * Update the URL according to the word and page specified.
		 * 
		 * @param query The search query
		 * @param page The page number
		 * @param include_related_forms Whether related forms should be included
		 * @param ignore_diacritics Whether diacritics should be ignored
		 */
		TextCritical.set_search_url = function ( query, page, include_related_forms, ignore_diacritics ) {
			
			// Get defaults for the arguments
			if(typeof include_related_forms === 'undefined'){
				var include_related_forms = false;
			}
			
			if(typeof ignore_diacritics === 'undefined'){
				var ignore_diacritics = false;
			}
			
			var params = {};
			
			// Add the related forms argument
			if( related_forms ){
				params['include_related'] = 1;
			}
			
			// Add the ignore diacritics argument
			if( ignore_diacritics ){
				params['ignore_diacritics'] = 1;
			}
			
			// Get the appropriate URL
			if( page <= 1 || parseInt(page) <= 1 ){
				params['q'] = query;
				page = 1;
			}
			else{
				params['q'] = query;
				params['page'] = page;
			}
			
			// Make the URL
			var url = document.location.pathname + "?" + $.param(params);
			
			// Push the state
			history.pushState( {query: query, page: page, include_related_forms:include_related_forms, ignore_diacritics:ignore_diacritics}, document.title, url);
		}
		
		/**
		 * Make a bar chart.
		 * 
		 * @param el The jQuery element that should contain the chart
		 * @param title The title of the chart
		 * @param categories An array of strings containing the categories
		 * @param data An array of numbers containing the data
		 */
		TextCritical.make_bar_chart = function ( el, title, results, no_data_message ) {
			
			// Provide a default for the no_data_message variable
			if(typeof no_data_message === 'undefined'){
				no_data_message = "No data matched";
			}
			
			// Process the data into what the charting library expects
			var categories = [];
			var data = [];
			
			if(results){
				for (var key in results) {
					  if (results.hasOwnProperty(key)) {
						  categories.push(key);
						  data.push(results[key])
					  }
					}
			}
			
			// Put up a message noting that no data was provided
			if(data.length === 0){
				el.html('<div class="alert alert-info alert-block">' + no_data_message + '</div>');
				return false;
			}
			
			// Make the chart
			el.highcharts({
				colors: ['#006dcc'],
		        chart: {
		            type: 'bar',
		            backgroundColor: '#2f2f2f',
		            width: $('.tab-pane.active').width()
		        },
		        title: {
		            text: title,
		        	style: { "color": "#DDD" }
		        },
		        legend:{
		        	enabled: false
		        },
		        xAxis: {
		            categories: categories,
		            title: {
		                text: null
		            },
		            labels: {
		            	style: { "color": "#DDD" }
		            },
		            lineColor: "#DDD",
		            tickColor: "#DDD"
		        },
		        yAxis: {
		            min: 0,
		            title: {
		                text: 'Count',
		                align: 'high'
		            },
		            labels: {
		                overflow: 'justify',
		                style: { "color": "#DDD" }
		            }
		        },
		        plotOptions: {
		            bar: {
		                dataLabels: {
		                    enabled: false
		                }
		            }
		        },
		        credits: {
		            enabled: false
		        },
		        series: [{
		            name: 'Count',
		            data: data
		        }]
		    });
			
		},
		
		/**
		 * Perform a search and render the results.
		 * Note: this users the blockUI jQuery plugin.
		 * 
		 * @param page The page number of the search results
		 * @param update_url A boolean indicating if the URL ought to be updated 
		 **/
		TextCritical.do_search = function ( page, update_url ) {
			
			// Get the word to search for
			var word = $("#search-term").val();
			
			// Get the page number
			if( typeof page == "undefined" || page == null ){
				
				if ( $("#page-number").val().length > 0 ){
					page = parseInt( $("#page-number").val() );
					console.info("Getting page from #page-number:" + $("#page-number").val());
				}
				else{
					page = 1;
					console.info("Setting page to 1");
				}
			}
			else{
				console.info("Using provided page: " + page );
			}
			
			// Determine if we are to search for related forms
			related_forms = $("#related_forms:checked").length;
			ignore_diacritics = $("#ignore_diacritics:checked").length;
			
			// Assign a default value to the update_url argument if it was not provided
			if( typeof update_url == 'undefined' ){
				update_url = true;
			}
			
			// Assign a default value to the related_forms argument if it was not provided
			if( typeof related_forms == "undefined" ){
				related_forms = 0;
			}
			else if (!related_forms){
				related_forms = 0;
			}
			else{
				related_forms = 1;
			}
			
			// Assign a default value to the ignore_diacritics argument if it was not provided
			if( typeof ignore_diacritics == "undefined" ){
				ignore_diacritics = 0;
			}
			else if (!ignore_diacritics){
				ignore_diacritics = 0;
			}
			else{
				ignore_diacritics = 1;
			}
			
			// Assign a value to the page number if it is not valid
			if( page <= 0 ){
				console.warn( "Page number is invalid (must be greater than zero)");
				page = 1;
			}
			
			// Set the data to store the page number
			$('#search-results-content').attr("data-page-number", page);
			
			$('#searching').show();
			//$('#search-results-content').hide();
			$('#search-results-content').block({ message: null, overlayCSS: { backgroundColor: '#2f2f2f', opacity: 0.8 } }); 
			
			console.info( "Executing search on page " + page + " for " + word );
			
			// Submit the AJAX request to display the information
			$.ajax({
				url: "/api/search/" + encodeURIComponent(word) + "?page=" + page + "&related_forms=" + related_forms + "&ignore_diacritics=" + ignore_diacritics
			}).done(function(search_results) {
				
				$("#search-results-content").html(_.template(search_results_template,{ word:_.escape(word), search_results:search_results }));
				
				// Setup the click handlers
				
				// If we have more pages, then setup the link to the "next" button		
				if( search_results.result_count > ( search_results.page * search_results.page_len ) ){
					$(".next-page-link").click( TextCritical.do_search_next );
				}
				
				// If we are not on the first page, then setup a link to go to the previous page
				if( search_results.page > 1 ){
					$(".previous-page-link").click( TextCritical.do_search_previous );
				}
				
				$('#search-results-content').unblock();
				console.info( "Successfully searched for " + word );
				
				// Make a bar chart of the word frequency
				TextCritical.make_bar_chart( $('#chart-word-frequency'), 'Frequency of matched words', search_results.matched_terms, "No data available on matched terms" );
				TextCritical.make_bar_chart( $('#chart-work-frequency'), 'Number of matched verses by work', search_results.matched_works, "No data available on matched works" );
				TextCritical.make_bar_chart( $('#chart-section-frequency'), 'Number of matched verses by section', search_results.matched_sections, "No data available on matched sections" );
				
				// Show the results and hide the "searching..." dialog
				$('#searching').hide();
				$('#search-results-content').show();
				
				if( update_url ){
					TextCritical.set_search_url(word, page, related_forms, ignore_diacritics);
				}
				
			}).error( function(jqXHR, textStatus, errorThrown) {
				$("#search-results-content").html( "<h4>Search failed</h4> The search request could not be completed" );
				console.error( "The request to search failed for " + word );
				
				$('#searching').hide();
				$('#search-results-content').show();
			});
			
			return false;
		}
		
		/**
		 * Do a search, starting from page 1.
		 **/
		TextCritical.do_fresh_search = function ( ) {
			return TextCritical.do_search( 1 );
		}
		
		/**
		 * Go to the next page in the search results.
		 **/
		TextCritical.do_search_next = function ( ) {
			return TextCritical.change_page( 1 );
		}
		
		/**
		 * Change to the page in the search results based on the offset provided. An offset of -1 goes back one page, an offset of 1 goes forward one.
		 * 
		 * @param offset The amount of change in the page number
		 */
		TextCritical.change_page = function ( offset ) {
			
			// Get the page number
			var page = parseInt( $('#search-results-content').attr("data-page-number") );
			
			if( typeof page == "undefined" ){
				page = 1;
			}
			else if( isNaN(page) ){
				console.warn( "Page number is invalid");
				page = 1;
			}
			else{
				page = page + offset;
			}
			
			TextCritical.do_search( page );
		}
		
		/**
		 * Go to search page to execute a search on the current work.
		 **/
		TextCritical.search_this_work = function ( ) {
			
			// Get the work that we are to search
			var work = $("h1[data-work-title-slug]").data("work-title-slug");
			
			// Make the URL
			var search_uri = "/search?q=work:" + work;
			
			// Get the current division name
			var division_data = $('#chapter-base-url').data();
			
			// Add on the division if available
			if(division_data){
				search_uri += ' section:"' + division_data.chapterDescription + '"';
			}
			
			// Go to the search page
			document.location = search_uri;
			return false;
		}
		
		/**
		 * Go to the previous page in the search results.
		 **/
		TextCritical.do_search_previous = function ( ) {
			return TextCritical.change_page( -1 );
		}
		
		/**
		 * Update the search results when the user presses the back button.
		 * 
		 * @param event The event from the popstate
		 **/
		TextCritical.search_page_popstate = function ( event ) {
			
			// Ignore events made from replace states
			if (event.state == null) {
				return;
			}
			  
			// Update the query if necessary
			$("#search-term").val( event.state.query );
			
			// Invoke the search, but don't update the URL (otherwise users will keep adding a new state and can never get back more than one)
			TextCritical.do_search( event.state.page, false );
		}
		
		/**
		 * Convert the beta-code to the associated Greek.
		 **/
		TextCritical.convert_search_query_beta_code = function ( ) {
			
			var query = $("#search-term").val();
			
			// Submit the AJAX request to display the information
			$.ajax({
				url: "/api/convert_query_beta_code/?q=" + query
			}).done(function(converted_query) {
				$("#search-term").val(converted_query);
			});
		}
		
		/**
		 * Add links to open the morphology dialog on the given text.
		 * 
		 * @param selector The selector that indicates where the processed text (which will include HTML) should go
		 * @param text The text to convert. If this is not provided, then the text will be gathered from the selector.
		 */
		TextCritical.add_word_morphology_links = function(selector, text){
			
			// If the user didn't provide the text, then assume we should change the existing text
			if(typeof text === 'undefined'){
				var text = selector.text();
			}
			
			var words = text.split(' ');

			// clear the existing content
			selector.text('');

			// insert each word wrapped with a span class to facilitate lookups
			for (var i = 0; i < words.length; i++)
			{
				selector.append('<span class="word">' + words[i] + ' </span>');
			}
		}
		
		/**
		 * Get the associated Greek forms.
		 **/
		TextCritical.get_related_forms = function( ) {
			
			query = encodeURIComponent($("#text").val());
			
			// Submit the AJAX request to display the information
			$.ajax({
				url: "/api/word_forms/" + query
			}).done(function(results) {
				$("#output").text(results.forms.join(", ").toLowerCase());
			});
		}
		
		/**
		 * Flatten the type-ahead hints
		 * 
		 * @param typeahead_hints The type-aheads hints to flatten
		 */
		TextCritical.flatten_typeahead_hints = function( typeahead_hints ){
	    	
	    	//Flatten the list so that Bootstrap typeahead can accept the list
	    	hints_flattened = [];
	    	
	    	for( var i = 0; i < typeahead_hints.length; i++){
				if( _.indexOf(hints_flattened, typeahead_hints[i].desc) < 0 ){
					hints_flattened.push( typeahead_hints[i].desc );
				}
			}
	    	
	    	return hints_flattened;
		}
		
		/**
		 *Store the type-ahead hints so that they can be reused.
		 */
		TextCritical.works_search_typeahead_hints = [];
		TextCritical.works_search_typeahead_hints_flattened = [];
		
		/**
		 * Retrieves a list of the typeahead hints used for the works list.
		 * 
		 * @param flattened A boolean indicating whether the list should be flattened
		 **/
		TextCritical.get_works_search_typeahead_hints = function ( flattened ) {
			
			var promise = jQuery.Deferred();
			
			if( typeof flattened == "undefined" ){
				var flattened = true;
			}
			
			// Get the list if it is already cached
			if( TextCritical.works_search_typeahead_hints_flattened.length > 0){
				console.info("Type-ahead hints already available via the cache")
				
				if( flattened ){
					promise.resolve(TextCritical.works_search_typeahead_hints_flattened);
				}
				else{
					promise.resolve(TextCritical.works_search_typeahead_hints);
				}
			}
			
			// Download the list otherwise
			else{
				console.info("Retrieving list of typeahead hints from the server");
				
				var promise = jQuery.Deferred();
				
		    	var request = $.ajax({
		  		  url: "/api/works_typeahead_hints",
		  		  success: function(html) {
		  			TextCritical.works_search_typeahead_hints = html;
		  			
		  			// Flatten the list so that Bootstrap typeahead can accept the list
		  			TextCritical.works_search_typeahead_hints_flattened = TextCritical.flatten_typeahead_hints(TextCritical.works_search_typeahead_hints);
		  			
		  			if( flattened ){
		  				promise.resolve(TextCritical.works_search_typeahead_hints_flattened);
		  			}
		  			else{
		  				promise.resolve(TextCritical.works_search_typeahead_hints);
		  			}
		  			
		  		  },
		  		  type: "GET"
		  		});
		    	
			}
			
	    	return promise;
		}
		
		/**
		 * Changes the url to go the work referenced by the given text provided that it only matches one item and the itme has a URL. Returns true if it has redirected.
		 * 
		 * @param text The text to search for
		 */
		TextCritical.jump_to_searched_text = function ( text ) {
			
			list = TextCritical.works_search_typeahead_hints;
			
			found = 0;
			url = null;
			
			// Try to find the item and also determine if the item is ambiguous (points to more than one item)
			for(var c = 0; c < list.length; c++ ){
				if( list[c].desc == text ){
					found = found + 1;
					url = list[c].url;
				}
			}
			
			// If we didn't find a URL or the information was ambiguous (referred to multiple items) then don't bother redirecting
			if( found > 1 || found == 0 || url == null || url == "" ){
				return false;
			}
			
			// Otherwise, redirect
			else{
				location = url;
				return true;
			}
		}
		
		/**
		 * Creates an alert message.
		 * 
		 * @param title The title of the message
		 * @param message The message to show
		 * @param level The level of the message (needs to be either 'error', 'info', or 'success')
		 **/
		TextCritical.show_alert = function ( title, message, level ) {
			
			if( typeof level == "undefined" || level == null ){
				level = 'info';
			}
			
			$("#messages").append(_.template(alert_message_template,{title:_.escape(title), message: _.escape(message), level: level}));
		}
		
		/**
		 * Updates the URL to point to the canonical URL for the work (if necessary).
		 * 
		 * @param work_url The new URL to use
		 **/
		TextCritical.update_work_url = function ( work_url ) {
			
			if( location.pathname !== work_url ){
				console.info("Updating the URL to reflect the canonical URL");
				title = document.title;
				history.replaceState( {}, title, work_url);
				
				TextCritical.show_alert( "Stale URL", "The URL you were using was old so redirected to the new one. You may want to update your shortcuts.",  "info");
			}
		}
		
		/**
		 * Get the content associated with the note with the target id.
		 * 
		 * @param target The name of the target ID from which the content of the note is to be extracted from
		 * @param shorten_to The length of the text to target to
		 * @param shorten_text The text of the note (for shortening)
		 **/
		TextCritical.get_note_content = function (target, shorten_to, shorten_text) {
			
			if( typeof shorten_to == undefined || shorten_to == null ){
				var shorten_to = false;
			}
			
			if( shorten_to > 0 ){
				content = TextCritical.shorten( $("#content_for_" + target).text(), shorten_to, true, shorten_text);
			}
			else{
				content = $("#content_for_" + target).html();
			}
			
			return content
		}
		
		/**
		 * Get the title associated with the note with the target id.
		 * 
		 * @param target The name of the target ID from which the title of the note is to be extracted from
		 **/
		TextCritical.get_note_title = function (target) {
			
			note_number = $("#" + target).attr("data-note-number");
			
			if( note_number != null){
		    	return "Note " + note_number;
			}
			else{
				return "Note";
			}
		}
		
		/**
		 * Opens the a dialog to show the note that was clicked.
		 * 
		 * @param note_element The ID of the associated note element
		 **/
		TextCritical.open_note_dialog = function ( note_element ) {
			
			title = TextCritical.get_note_title( $(this).attr("id") );
			content = TextCritical.get_note_content( $(this).attr("id") );
			
			TextCritical.open_dialog( title, content );
			return false;
		}
		
		/**
		 * Escape a string such that it can be inserted into a regular expression.
		 * 
		 * @param str A string that needs to be escaped since it may include regular expression characters 
		 */
		TextCritical.escape_regex = function ( str ) {
			  return str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&");
		}
		
		/**
		 * Highlight all of the words
		 */
		TextCritical.highlight_searched_terms = function(){
			
			 var search_highlights = TextCritical.get_parameter_by_name(document.location.search, "highlight", true);
			 
			 if(search_highlights !== undefined){
				 for(var c = 0; c < search_highlights.length; c++){
					 TextCritical.highlight_word(decodeURIComponent(search_highlights[c]), "searched", false);
				 } 
			 }
		}
		
		/**
		 * Get the parameter from the query string.
		 * 
		 * @param url The URL containing the GET parameter
		 * @param name The name of the parameter to obtain
		 * @param return_as_array Return an array containing all instances of the argument
		 */
		TextCritical.get_parameter_by_name = function ( url, name, return_as_array ) {
			
			if(typeof return_as_array == 'undefined'){
				var return_as_array = false;
			}
			
		    name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
		    
		    var regex = new RegExp("[\\?&]" + name + "(=([^&#]*))?", "g");
		    
		    var results;
		    var parameter_values = [];
		    
		    while(results = regex.exec(url)){
			    
			    // Parameter was found and has a value
			    if(results[2] !== undefined){
			    	parameter_values.push(results[2].replace(/\+/g, " "));
			    }
			    
			    // Parameter was found and has no value
			    else{
			    	parameter_values.push("");
			    }
			    
			    // If only returning one value, then stop
			    if(!return_as_array){
			    	return parameter_values[0];
			    }
		    }
		    
		    // Return the results
		    if(parameter_values.length == 0){
		    	return undefined;
		    }
		    else{
		    	return parameter_values;
		    }
		    
		}
		
		/**
		 * Add the parameter 'async' to the URL to note that it is the results of an asynchronous request for content to be placed in another part of the page.
		 * 
		 * @param url The url to add the parameter to
		 */
		TextCritical.add_async_parameter = function ( url ){
			
			// Add the async parameter (if it doesn't already exist)
			if( TextCritical.get_parameter_by_name(url, "async") !== undefined ){
				// Don't bother adding the async parameter, it already exists
			}
			else if( url.indexOf("?") > 0 ){
				url = url + "&async";
			}
			else{
				url = url + "?async";
			}
			
			return url;
			
		}
		
		/**
		 * Loads the content from the given URL and loads it into the location where content goes (#main-content).
		 * 
		 * @param url The URL to grab the content with
		 **/
		TextCritical.load_ajah = function ( url ) {
			
			// Add the async parameter (if it doesn't already exist)
			url = TextCritical.add_async_parameter(url);
			
			// Perform the AJAX request
			$.ajax({
				    url: url,
				    success: function(data){
				    	console.info("Loading page content with asynchronous request");
				        $('#main-content').html(data).fadeIn('slow');
				        $("#async-loading-message").hide();
				        console.info("Sucessfully loaded page content with asynchronous request");
				        
				    },
				    error:  function(jqXHR, textStatus, errorThrown){
				    	console.error("Failed to load the page content with asynchronous request");
				        $('#main-content').html("<h3>Yikes! That didn't work</h3>I'm sorry, but the content couldn't be loaded").fadeIn('slow');
				        $("#async-loading-message").hide();
				    }
			});
		}
		
		/**
		 * Load the link reference in next link tag so that it gets cached and loads quickly if user continues to the next chapter.
		 */
		TextCritical.pre_load_next_link = function ( ) {
			
			// Get the link to the next page
			next_href = $("link[rel=next]").attr("href");
			
			// If the page has a link to the next page, cache it
			if( next_href !== undefined ){
				
				// Add the async parameter since this content is presumably AJAX content
				next_href = TextCritical.add_async_parameter(next_href);
				
				// Do an AJAX request so that the next chapter is cached
				console.info("Beginning request to cache content of the next chapter (" + next_href + ")");
				
				// Perform the request
				$.ajax({
					url: next_href
				}).done(function(data) {
					// Successfully loaded the content
					console.info( "Successfully cached the contents of the next chapter at " + next_href );
				}).error( function(jqXHR, textStatus, errorThrown) {
					// The content could not be loaded
					console.error( "Request for next chapter's content failed (url attempted was " + next_href + ")");
				});
				
			}
			
		}
		
		/**
		 * Convert the beta-code to Unicode.
		 * 
		 * @param beta_code The beta-code to convert to Greek
		 **/
		TextCritical.convert_search_query_beta_code = function ( beta_code) {
			
			converted_beta_code = null;
			
			// Submit the AJAX request to convert the beta-code
			$.ajax({
				async: false,
				url: "/api/beta_code_to_unicode/?text=" + beta_code
			}).done(function(response) {
				converted_beta_code = response.unicode;
			});
			
			return converted_beta_code;
		}
		
		/**
		 * Freeze the height of the given object.
		 * 
		 * @param selector The selector of the panel to freeze the height for
		 **/
		TextCritical.freeze_height = function(selector){
			
			$(selector).css("height", $(selector).height());
		}
		
		/**
		 * Unfreeze the height of the given object.
		 * 
		 * @param selector The selector of the panel to un0freeze the height for
		 **/
		TextCritical.unfreeze_height = function(selector){
			
			$(selector).css("height", "auto");
		}
		
		/**
		 * Return true if any of the HTML5 data attributes contain the given text.
		 * 
		 * @param attributes The attributes to analyze (a NamedNodeMap)
		 * @param text The text to search for
		 */
		TextCritical.data_attribute_contains = function(attributes, text) {
			
			for(var i=0; i<attributes.length; i++){
				
				attribute = attributes[i];
				
				// Make sure that attribute is an HTML 5 data attribute
				if( attribute.name.indexOf("data-") == 0 ){
					if( attribute.value.toLowerCase().indexOf(text) >= 0 ){
						return true;
					}
				}
			}
			
			return false;
		}
		
		/**
		 * Setup a filter a list based on the contents of an input box
		 * 
		 * @param input The input box to get the filter text from
		 * @param list The list to filter
		 **/
		TextCritical.list_filter = function(input, list, freeze_height) {
			
			// Do not freeze the height of the div by default
			if( typeof freeze_height == "undefined" ){
				var freeze_height = false;
			}

			$(input).change( function () {
			    	  
				// Get the text to filter on; convert it to lower case so that we can do case insensitive matching
			    var filter = $(this).val().toLowerCase();
			        
			    // Filter the list
			    if(filter) {
			        	
			    	// Freeze the height of the list
			    	if( freeze_height ){
			          TextCritical.freeze_height(list);
			    	}
			          
			    	// Find the items to hide:
			    	$(list).find('a').each(function(i) {
			        	
			    		// If the text of the link matches, show it
			    		if( $(this).text().toLowerCase().indexOf(filter) >= 0){
			    			$(this).parent().show();
			        	}
			    		else if( TextCritical.data_attribute_contains( this.attributes, filter) ){
			        		$(this).parent().show();
			        	}
			    		else{
			    			$(this).parent().hide();
			    		}
			        });
			          
			    } else {
			    	$(list).find("li").show();
			          
			         if( freeze_height ){
			        	 TextCritical.unfreeze_height(list);
			         }
			    }
			        return false;
			}).keyup( function () {
			        // fire the above change event after every letter
			        $(this).change();
			});
		}
		
		/**
		 * Get the URL to the referenced item
		 * 
		 * @param work_title_slug the title slug for the document containing the reference
		 * @param reference the reference to find the URL for
		 **/
		TextCritical.resolve_path = function(work_title_slug, reference) {
			
			var reference_url = null;
			
			var request = $.ajax({
		  		  url: "/api/resolve_reference/?work=" + work_title_slug + "&ref=" + reference,
		  		  async : false,
		  		  success: function(reference) {
		  			reference_url = reference.url;
		  		  },
		  		  type: "GET"
		  	});
			
			return reference_url;
			
		}
		
		/**
		 * Initialize the Facebook API
		 */
		TextCritical.facebookInit = function() {
			
			if(typeof FB !== "undefined"){
		        // init the FB JS SDK
		        FB.init({
		          appId      : '226685657481279', // App ID from the app dashboard
		          xfbml      : true               // Look for social plugins on the page
		        });
			}
		}
		
		/**
		 * If the provided text is not appropriate for sharing, then autodiscover the content to share. This will also do some cleanup on the text, like:
		 * 
		 *  1) Trimming whitespace
		 *  2) Removing wierd endlines
		 * 
		 * @param text Some text that may be shared
		 * @param give_selection_precedence If true, highlighted text will be used instead of the provided content (if highlighted text is available)
		 */
		TextCritical.getTextToShare = function(text, give_selection_precedence){

			if( typeof text === "undefined" || text == null){
				var text = "";
			}
			
			// If the text was not defined, then find a way to discover it automatically
			if( TextCritical.trim(text).length == 0 || give_selection_precedence === true){
				
				// Try to get the selected text
				if( window.getSelection().toString().length > 0){
					text = window.getSelection().toString();
				}
			}
			
			// Trim the text
			text = TextCritical.trim(text);
				
			// Remove endlines
			text = text.replace(/[ ]*\n[ ]*/g, ' ');
			
			return text
		}
		
		/**
		 * If the given string (presumably representing a url) ends with a #, then remove it.
		 * 
		 * @param str A string that may have a trailing #
		 */
		TextCritical.trimTrailingPound = function( str ){
			if( str.slice(-1) == "#" ){
				return str.slice(0, str.length-2)
			}
			else{
				return str;
			}
		}
		
		/**
		 * Make a Facebook post.
		 * 
		 * @param caption The caption of the link (appears beneath the link name)
		 * @param description The description of the link (appears beneath the link caption)
		 * @param give_selection_precedence If true, highlighted text will be used instead of the provided content (if highlighted text is available)
		 * @param link The link attached to this post
		 * @param name The name of the link attachment
		 */
		TextCritical.postToFacebook = function(caption, description, give_selection_precedence, link, name){
			
			// If the link was not defined, then use the current URL
			if( typeof link === "undefined" || link == null ){
				var link = location.href;
			}
			
			// If the name was not defined, then use the document title
			if( typeof name === "undefined" || name == null ){
				var name = document.title;
			}
			
			// If the text was not defined, then find a way to discover it automatically
			description = TextCritical.getTextToShare(description, give_selection_precedence);
			
			FB.ui({
		    	  method: 'feed',
		    	  link: TextCritical.trimTrailingPound(link),
		    	  name: name,
		    	  caption: caption,
		    	  description: TextCritical.shorten(description, 400, true, "...")
			}, function(response){});
		}
		
		/**
		 * Make a URL for sending a Tweet.
		 * 
		 * @param link The link to tweet
		 * @param text The text to share
		 * @param give_selection_precedence If true, highlighted text will be used instead of the provided content (if highlighted text is available)
		 */
		TextCritical.makeTweetURL = function( link, text, give_selection_precedence ){
			
			// If the link was not defined, then use the current URL
			if( typeof link === "undefined" || link == null ){
				var link = location.href;
			}
			
			// If the text was not defined, then find a way to discover it automatically
			text = TextCritical.getTextToShare(text, give_selection_precedence);
			
			// This is the base part of the URL
			twitterLink = 'https://twitter.com/share';
			
			// Make up the arguments and assemble the URL
			data = {
					url : TextCritical.trimTrailingPound(link),
					text: TextCritical.shorten(text, 140 - link.length, true, "...")
			}
			
			return twitterLink + '?' + $.param(data);
		}
		
		/**
		 * Make a Twitter tweet.
		 * 
		 * @param text The text to share
		 * @param give_selection_precedence If true, highlighted text will be used instead of the provided content (if highlighted text is available)
		 * @param link The link to tweet
		 */
		TextCritical.postToTwitter = function(text, give_selection_precedence, link){
			twitterLink = TextCritical.makeTweetURL(link, text, give_selection_precedence);
			window.open(twitterLink,'_blank');
		}
		
		/**
		 * Serialize the provided object to a URL.
		 * 
		 * @param obj The object to serialize to a URL.
		 */
		TextCritical.serialize = function(obj) {
			  var str = [];
			  for(var p in obj)
			     str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
			  return str.join("&");
		}
		
		/**
		 * Send an email.
		 * 
		 * @param subject The subject of the email
		 * @param body The body of the email
		 * @param give_selection_precedence If true, highlighted text will be used instead of the provided content (if highlighted text is available)
		 * @param link The link to the content
		 */
		TextCritical.sendAnEmail = function(subject, body, give_selection_precedence, link){
			
			// If the link was not defined, then use the current URL
			if( link === undefined || link == null ){
				link = location.href;
			}
			
			// If the subject was not defined, then use the current document title
			if( subject === undefined || link == null ){
				subject = document.title;
			}
			
			// If the text was not defined, then find a way to discover it automatically
			body = TextCritical.getTextToShare(body, give_selection_precedence);
			
			// Make up the arguments and assemble the URL
			data = {
					subject : subject,
					body    : TextCritical.shorten(body, 1000, true, "...") + "\n\n[Source: " + TextCritical.trimTrailingPound(link) + "]",
					
			}
			
			// Open the email link
			document.location.href = "mailto:" + '?' + TextCritical.serialize(data);
		}
		
		/**
		 * The Twitter and Facebook APIs take a second or two to make the share buttons. Thus, they are hidden by default and are only shown once the content is available.
		 */
		TextCritical.pollForShareButtons = function(){
			
			if( $('iframe', '.sharing-buttons').length < 2 ){
				setTimeout( TextCritical.pollForShareButtons , 200);
			}
			else{
				// Now that iframes exist, give it another second or so to render before showing them
				setTimeout(function(){ $('.sharing-buttons').fadeIn(); } , 1500);
			}
		}
		
		

}
);