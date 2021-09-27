function showload() {
	var element1 = document.getElementById("collect_button");
	element1.classList.add('animate_button');
	element1.innerHTML = "Сбор комменатриев...";

}

function read_client_timezone() {
	var timezone_element = document.getElementsByName("client_timezone");
/* 	var offset = new Date(); */
	timezone_element[0].value = Intl.DateTimeFormat().resolvedOptions().timeZone;
}

function changemode(to_mode) {
	var by_posts_count_button = document.getElementById("by_posts_count");
	var by_date_button = document.getElementById("by_date");
	var request_mode_input = document.getElementsByName("request_mode");
	var posts_count_input = document.getElementsByName("posts_count");
	var posts_offset_input = document.getElementsByName("posts_offset");
	var request_start_date_input = document.getElementsByName("request_start_date");
	var request_end_date_input = document.getElementsByName("request_end_date");
	if (to_mode === 1) {
		by_date_button.disabled = true
		by_posts_count_button.disabled = false
		request_mode_input[0].value = 1
		posts_count_input[0].hidden = true
		posts_offset_input[0].hidden = true
		request_start_date_input[0].hidden = false
		request_end_date_input[0].hidden = false
	}
	
	if (to_mode === 0) {
		by_date_button.disabled = false
		by_posts_count_button.disabled = true
		request_mode_input[0].value = 0
		posts_count_input[0].hidden = false
		posts_offset_input[0].hidden = false
		request_start_date_input[0].hidden = true
		request_end_date_input[0].hidden = true
	}
}

	  
