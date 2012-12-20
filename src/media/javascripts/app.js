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
    	divisions_map[division_ids[c]] = TextCritical.slugify(division_ids[c]);
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
 **/
TextCritical.go_to_chapter = function( reference, division_ids ){
	document.location = TextCritical.resolve_path(reference, division_ids);
}