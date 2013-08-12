/* Author: Luke Murphey

*/

var TextCritical = {};

define([
        'jquery',
        'underscore',
        'libs/text!/media/templates/alert_message.html',
        'libs/text!/media/templates/morphology_dialog.html',
        'libs/text!/media/templates/loading_dialog.html',
        'libs/text!/media/templates/search_results.html'
    ],
    function($, _, alert_message_template,  morphology_dialog_template, loading_template, search_results_template) {
	
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
			
			if( scrollTo == undefined ){
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
			if ( base_chapter_url == null || base_chapter_url == undefined ){
				console.warn("No base chapter URL was provided; will not be able to update the URL for the given verse");
				return true; // Let the href propagate
			}
			
			// The ID of the verse number element
			var id = "verse-" + verse_number;
			var escapted_id = TextCritical.escapeIdentifier(id);
			
			// Update the URL
			title = document.title;
			history.pushState( {verse: verse_number}, title, base_chapter_url + "/" + verse_number);
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
			
			work = $("h1[data-work-title-slug]").data("work-title-slug");
			
			TextCritical.open_morphology_dialog( $(this).text(), work );
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
			
			if ( extra_options == null || extra_options == undefined ){
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
		TextCritical.open_morphology_dialog = function ( word, work ) {
		
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
				$("#popup-dialog-content").html(_.template(morphology_dialog_template,{parses:data, word: _.escape(word), work: work}));
		
				// Set the lemmas to be links
				$("a.lemma").click(TextCritical.word_lookup);
		
				console.info( "Successfully performed a request for the morphology of " + word );
		
			}).error( function(jqXHR, textStatus, errorThrown) {
				$("#popup-dialog-content").html( "<h4>Parse failed</h4> The request to parse could not be completed" );
				console.error( "The request for the morphology failed for " + word );
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
		 * @param a the desired length
		 * @param use_word_boundary if true, then the string will be shortened while attempting to avoid a break in a word
		 * @param shorten_text the text to add if the string is shortened
		 */
		TextCritical.shorten = function(s, n, use_word_boundary, shorten_text){
			
			if( shorten_text == undefined || shorten_text == null ){
				shorten_text = '&hellip;';
			}
			
			if( use_word_boundary == undefined || use_word_boundary == null ){
				use_word_boundary = true;
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
		TextCritical.unhighlight_all_words = function () {
			$('.word').removeClass('highlighted');
		}
		
		/**
		 * Highlights all of the word nodes with the given text.
		 * 
		 * @param word The word to highlight
		 */
		TextCritical.highlight_word = function ( word ) {
			
			// Unhighlight all existing words to make sure we don't accumulate highlights
			TextCritical.unhighlight_all_words();
			
			// Make the regular expression for finding the words
			escaped_word = TextCritical.escape_regex(word);
			var pattern = new RegExp("^" + escaped_word + "$");
			console.info( "Highlighting " + word );
			
			// Add the CSS to make these words highlighted
			$('.word').filter(function(){
		  		return pattern.test($(this).text())
			}).addClass('highlighted');
		}
		
		/**
		 * Determine if the results has actual words to kick off a search to look for (other than just the parts of the search specifying
		 * the work to search).
		 * 
		 * @param query The query to perform a search on
		 **/
		TextCritical.contains_search_words = function ( query ) {
			split_query = query.match(/([_0-9a-z]+[:][-_0-9a-z]+)|([\w_]+[:]["][-\w ]*["])|([^ :]+)/gi);
			
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
		 */
		TextCritical.set_search_url = function ( query, page ) {
			
			// Get the appropriate URL
			if( page <= 1 || parseInt(page) <= 1 ){
				url = document.location.pathname + "?&q=" + query;
				page = 1;
			}
			else{
				url = document.location.pathname + "?q=" + query + "&page=" + page;
			}
			
			// Push the state
			history.pushState( {query: query, page: page}, document.title, url);
		}
		
		/**
		 * Perform a search and render the results.
		 * Note: this users the blockUI jQuery plugin.
		 * 
		 * @param page The page number of the search results
		 * @param update_url A boolean indicating if the URL ought to be updated 
		 **/
		TextCritical.do_search = function ( page, update_url ) {
			
			// Get the word to search for
			word = $("#search-term").val();
			
			// Get the page number
			if( page == undefined || page == null ){
				
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
			
			// Determined if we are to search for related forms
			related_forms = $("#related_forms:checked").length;
			
			// Assign a default value to the update_url argument if it was not provided
			if( update_url == undefined ){
				update_url = true;
			}
			
			// Assign a default value to the related_forms argument if it was not provided
			if( related_forms == undefined ){
				related_forms = 0;
			}
			else if (!related_forms){
				related_forms = 0;
			}
			else{
				related_forms = 1;
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
				url: "/api/search/?q=" + encodeURIComponent(word) + "&page=" + page + "&related_forms=" + related_forms
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
				
				// Show the results and hide the "searching..." dialog
				$('#searching').hide();
				$('#search-results-content').show();
				
				if( update_url ){
					TextCritical.set_search_url(word, page);
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
		 * Show or hide the search help depending on the parameter (by default, it shows it).
		 * 
		 * @param show A boolean indicating whether the search help should be shown
		 */
		TextCritical.show_search_help = function ( show ) {
		
			if( show == undefined ){
				show = true;
			}
			
			if( show ){
				$("#search-help").show();
				$('#search-results-content').hide();
			}
			else{
				$("#search-help").hide();
				$('#search-results-content').show();
			}
		}
		
		/**
		 * Show the search help if it is not shown; hide it otherwise.
		 */
		TextCritical.toggle_search_help  = function ( ) {
			
			if( $("#search-help").is(":visible") ){
				TextCritical.show_search_help( false );
			}
			else{
				TextCritical.show_search_help( true );
			}
			
			return false;
			
		}
		
		/**
		 * Do a search, starting from page 1.
		 **/
		TextCritical.do_fresh_search = function ( ) {
			TextCritical.show_search_help( false );
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
			page = parseInt( $('#search-results-content').attr("data-page-number") );
			
			if( page == undefined ){
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
			work = $("h1[data-work-title-slug]").data("work-title-slug");
			
			// Make the URL
			search_uri = "/search?q=work:" + work;
			
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
		 * Update the search results when the user presses the back button.
		 **/
		TextCritical.convert_search_query_beta_code = function ( ) {
			
			query = $("#search-term").val();
			
			// Submit the AJAX request to display the information
			$.ajax({
				url: "/api/convert_query_beta_code/?q=" + query
			}).done(function(converted_query) {
				$("#search-term").val(converted_query);
			});
		}
		
		/**
		 * Retrieves a list of the typeahead hints used for the works list.
		 **/
		TextCritical.works_search_typeahead_hints = [];
		
		TextCritical.get_works_search_typeahead_hints = function ( ) {
			
			if( TextCritical.works_search_typeahead_hints.length > 0){
				return TextCritical.works_search_typeahead_hints;
			}
			else{
				console.info("Retrieving list of typeahead hints from the server");
		    	var request = $.ajax({
		  		  url: "/api/works_typehead_hints",
		  		  async : false,
		  		  success: function(html) {
		  			TextCritical.works_search_typeahead_hints = html;
		  		  },
		  		  type: "GET"
		  		});
		    	
		    	return TextCritical.works_search_typeahead_hints;
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
			
			if( level == undefined || level == null ){
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
			
			if( shorten_to == undefined || shorten_to == null ){
				shorten_to = false;
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
		 * Get the parameter from the query string.
		 * 
		 * @param url 
		 * @param name The name of the parameter to obtain
		 */
		TextCritical.get_parameter_by_name = function ( url, name ) {
		    name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
		    
		    var regex = new RegExp("[\\?&]" + name + "(=([^&#]*))?"),
		        results = regex.exec(url);
		    
		    // Parameter was not found
		    if (results == null){
		    	return undefined;
		    }
		    
		    // Parameter was found and has a value
		    else if(results[2] !== undefined){
		    	return results[2].replace(/\+/g, " ");
		    }
		    
		    // Parameter was found and has no value
		    else{
		    	return "";
		    }
		}
		
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
		 * This function sets up links such that apps saved locally don't open Safari for links. 
		 * 
		 * For more informtaion see: http://stackoverflow.com/questions/2898740/iphone-safari-web-app-opens-links-in-new-window
		 */
		TextCritical.setup_link_handlers_for_ios_web_apps = function ( ) {
			
			if (("standalone" in window.navigator) && window.navigator.standalone) {
			     
				// Use a delegated event handler so that new content added via AJAX is handled properly
				$(document).on('click', 'a', function(e){
			        
					var href = $(this).attr("href");
					
					// Don't override links that:
					// 1) Have a target of _blank (and should open in a new window)
					// 2) Are for external domains
					
					if( e.target.target != "_blank" && (href.indexOf(location.hostname) > -1 || href.indexOf("http") != 0 ) ){
						
						e.preventDefault();
				        
				        var new_location = href;
				        
				        // Stop on undefined links, local handlers (#) and Bootstrap links
				        if (new_location != undefined && new_location.substr(0, 1) != '#' && $(this).attr('data-method') == undefined){
				        	window.location = new_location;
				        }
					}
			    });
			 }
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
		
		TextCritical.freeze_height = function(selector){
			
			$(selector).css("height", $(selector).height());
		}
		
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
			if( freeze_height == undefined ){
				freeze_height = false;
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

}
);