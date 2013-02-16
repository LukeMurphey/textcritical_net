/* Author: Luke Murphey

*/

var TextCritical = {};

/**
 * Causes the verses to break onto separate lines. 
 **/
TextCritical.setFormatBreakLine = function(){
	$('.verse_container').addClass("block");
	$('#align_break').addClass('active');
}

/**
 * Causes the verses to not break onto separate lines. 
 **/
TextCritical.unSetFormatBreakLine = function(){
	$('.verse_container').removeClass("block");
	$('#align_break').removeClass('active');
}

/**
 * Toggles the table-of-contents.
 **/
TextCritical.toggleTOC = function(){
	$('.table_of_contents').toggle('fast', 'swing');
}

/**
 * Toggles the verse breaks.
 **/
TextCritical.toggleVerseBreak = function(){
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
 * Scrolls to the given anchor.
 **/
TextCritical.scrolltoAnchor = function(id){
	$('html,body').animate({scrollTop: $("#"+id).offset().top},'slow');
}

/**
 * Highlight a selected verse without performing a request to the server.
 **/
TextCritical.scrollToVerse = function(verse_number, base_chapter_url){

	// Make sure a base chapter URL was provided
	if ( base_chapter_url == null || base_chapter_url == undefined ){
		console.warn("No base chapter URL was provided; will not be able to update the URL for the given verse");
		return true; // Let the href propagate
	}
	
	// The ID of the verse number element
	var id = "verse_" + verse_number
	
	// Update the URL
	title = document.title;
	history.pushState( {verse: verse_number}, title, base_chapter_url + "/" + verse_number);
	console.info("Updating the URL to point to the selected verse");
	
	// Remove existing highlights
	$('.verse_container').removeClass('highlighted');
	$('.verse.number').removeClass('label-info');
	
	// Highlight the new verse
	$('#' + id).addClass('highlighted');
	$('#' + id + ' .label').addClass('label-info');
	
	// Scroll to the verse
	TextCritical.scrolltoAnchor(id);
	
	return false; // Stop the page from reloading
	
}

/**
 * Loads the client-saved settings.
 **/
TextCritical.loadStoreSettings = function(){
	
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
 * @param string The text to slugify.
 **/
TextCritical.slugify = function (text) {
	text = text.replace(/[^-a-zA-Z0-9,&\s]+/ig, '');
	text = text.replace(/-/gi, "_");
	text = text.replace(/\s/gi, "-");
	return text;
}

/**
 * Determines the path that corresponds to the given reference.
 * 
 * @param string the reference to go to (like "Romans 14:1")
 * @param array an array of the current division markers. Used to help the function not break on division descriptors that have spaces in the name (like "1 Thessalonians")
 **/
TextCritical.resolve_path = function( reference, division_ids ){
	
	// Trim the reference in case it has extra spaces and change to lower case so that we handle reference in a case insensitive way
	reference = TextCritical.trim( reference ).toLowerCase();
	
	// Change all of the division IDs to lower case
	for( c = 0; c < division_ids.length; c++ ){
		division_ids[c] = division_ids[c].toLowerCase();
	}
	
    // Break up the path
    var path_array = window.location.pathname.split( '/' );
    var path = [];
    
    for( i = 0; i < path_array.length; i++){
    	if( path_array[i].length > 0 ){
    		path.push(path_array[i]);
    	}
    	
    	if( path.length >= 2 ){
    	   break;
    	}
    }
        
    // Make a map from division IDs so that we avoid breaking on division IDs with spaces in them
    divisions_map = {}
    
    for( c = 0; c < division_ids.length; c++ ){
    	
    	// Set the key to the be the slugified version of the division ID
    	divisions_map[division_ids[c]] = TextCritical.slugify(division_ids[c]);
    	
    	// Set the value to be the original
    	reference = reference.replace(division_ids[c], TextCritical.slugify(division_ids[c]));
    }
    
    // Break up the reference entry
    refs = reference.split(/[ :._]+/);
    
    // Swap the slugs back with the originals
    for(var original_name in divisions_map){
    	for( c = 0; c < refs.length; c++){
    		refs[c] = refs[c].replace(divisions_map[original_name], original_name)
    	}
    }
    
    // Make the path
    return "/" + path.concat(refs).join("/");
}

/**
 * Opens the view to the given chapter reference.
 * 
 * @param string the reference to go to (like "Romans 14:1")
 * @param array an array of division IDs; these will be used to help parsing of the reference
 **/
TextCritical.go_to_chapter = function( reference, division_ids ){
	document.location = TextCritical.resolve_path(reference, division_ids);
}

/**
 * Opens the morphology dialog on the word within the text clicked.
 **/
TextCritical.word_lookup = function (){
	
	work = $("h1[data-work-title-slug]").data("work-title-slug");
	
	TextCritical.open_morphology_dialog( $(this).text(), work );
	return false;
}

/**
 * Opens a dialog that obtains the morphology of a word.
 **/
TextCritical.open_morphology_dialog = function( word, work ){
	
	console.info( "Obtaining the morphology of " + word );
	
	// Trim the word in case extra space was included
	word = TextCritical.trim(word);
	
	// Reset the content to the loading content
	var loading_template = $("#morphology-loading").html();
	$("#morphology-dialog-content").html(_.template(loading_template,{ message: "Looking up morphology for " +  _.escape(word) + "..." }));
	
	// Set the link to Google
	var extra_options_template = 'Look up at <a target="_blank" href="http://www.perseus.tufts.edu/hopper/morph?l=<%= word %>&la=greek">Perseus</a> or <a target="_blank" href="https://www.google.com/search?q=<%= word %>">Google</a>';
	
	$("#morphology-dialog-extra-options").html(_.template(extra_options_template,{ word : word }));
	
	// Set the title
	$("#morphology-dialog-label").text("Morphology: " +  _.escape(word) );
	
	// Open the form
	$("#morphology-dialog").modal();
	
	// Submit the AJAX request to display the information
	$.ajax({
		url: "/api/word_parse/" + word
	}).done(function(data) {
		
		// Render the lemma information
		var template = $("#morphology-info").html();
		$("#morphology-dialog-content").html(_.template(template,{parses:data, word: _.escape(word), work: work}));
		
		// Set the lemmas to be links
		$("a.lemma").click(TextCritical.word_lookup);
		
		console.info( "Successfully performed a request for the morphology of " + word );
		
	}).error( function(jqXHR, textStatus, errorThrown) {
		$("#morphology-dialog-content").html( "<h4>Parse failed</h4> The request to parse could not be completed" );
		console.error( "The request for the morphology failed for " + word );
	});
}

/**
 * Trims the string.
 * @param s the string to be stripped
 */
TextCritical.trim = function(s) 
{
    return String(s).replace(/^\s+|\s+$/g, '');
}

/**
 * Highlights the word that the user is focusing on or hovering over.
 **/
TextCritical.highlight_selected_word = function(){
	TextCritical.highlight_word( $(this).text() );
}

/**
 * Unhighlights all words.
 */
TextCritical.unhighlight_all_words = function(){
	$('.word').removeClass('highlighted');
}

/**
 * Highlights all of the word nodes with the given text.
 * @param word the word to highlight
 */
TextCritical.highlight_word = function( word ){
	
	// Unhighlight all existing words to make sure we don't accumulate highlights
	TextCritical.unhighlight_all_words();
	
	// Make the regular expression for finding the words.
	var pattern = new RegExp("^" + word + "$");
	console.info( "Highlighting " + word );
	
	// Add the CSS to make these words highlighted
	$('.word').filter(function(){
  		return pattern.test($(this).text())
	}).addClass('highlighted');
}

/**
 * Determine if the results has actual words to kick off a search to look for (other than just the parts of the search specifying
 * the work to search).
 **/
TextCritical.contains_search_words = function( query ){
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
 **/
TextCritical.set_caret_at_end = function(elem) {
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
 */
TextCritical.set_search_url = function( query, page ){
	
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
 **/
TextCritical.do_search = function( page, update_url ){
	
	word = $("#search-term").val();
	
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
	
	if( update_url == undefined ){
		update_url = true;
	}
	
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
		url: "/api/search/?q=" + word + "&page=" + page
	}).done(function(search_results) {
		
		var search_results_template = $("#search-results").html();
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
 * Do a search, starting from page 1.
 **/
TextCritical.do_fresh_search = function( ){
	return TextCritical.do_search( 1 );
}

/**
 * Go to the next page in the search results.
 **/
TextCritical.do_search_next = function( ){
	return TextCritical.change_page( 1 );
}

/**
 * Change to the page in the search results based on the offset provided. An offset of -1 goes back one page, an offset of 1 goes forward one.
 */
TextCritical.change_page = function( offset ){
	
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
 * Go to the previous page in the search results.
 **/
TextCritical.do_search_previous = function( ){
	return TextCritical.change_page( -1 );
}


/**
 * Update the search results when the user presses the back button.
 **/
TextCritical.search_page_popstate = function( event ){
	
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
TextCritical.convert_search_query_beta_code = function( ){
	
	query = $("#search-term").val();
	
	// Submit the AJAX request to display the information
	$.ajax({
		url: "/api/convert_query_beta_code/?q=" + query
	}).done(function(converted_query) {
		$("#search-term").val(converted_query);
	});
}