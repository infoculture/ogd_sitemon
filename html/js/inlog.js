$(document).ready(function(){ 
	// PNG FIX
	$('img').pngFix();
	
	// SYSTEM MESSAGES
	$("div.message img").click(function () {
      $(this).parent().closest('div.message').fadeOut();
    });
	
	$('.row select').sbCustomSelect();
});