function init() {
	$("#form").submit(submit);
	$("#styles").loadSelect("styles").val("apa");
	$("#locales").loadSelect("locales").val("en-US");
	$("#styles").combobox();
	$("#locales").combobox();

	(new URL(window.location.href)).searchParams.forEach((x, y) =>
		document.getElementById(y).value = x);

	new Clipboard('.btn-lg');
	// TODO: there is an issue in order to get plain-text right-of-thebox in github https://github.com/zenorocha/clipboard.js/issues/299
	$("#citation_row").hide();
	// $("#copy_citation").hide();
}


function submit() {
	$("#citation_row").hide();
	var dap_url = $("#dap_url").val().trim();
	$.ajax({
		url : "/citations/snippet",
		data : {
			dap_url : dap_url,
			format : $("#format").val()
		},
		dataType : "text",
		success : function(data) {
		    $("#citation").val(data);
            M.textareaAutoResize($('#citation'));

			$("#citation_row").show();
		},
		error : function(jqXHR, textStatus, errorThrown) {
			$("#citation_row").hide();
			alert(jqXHR.responseText);
		}
	});
	return false;
}



$(document).ready(init);
