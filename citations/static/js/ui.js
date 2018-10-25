function init() {
	$("#formatCitation").submit(updateCitationRow);
	$("#formatForm").submit(updateCitationRow);
    stylesAutocomplete();
	$("#doiCol").hide();
	$("#citation_row").hide();
	$("#externalDOI").change(toggleExternalDoiRadio);
	$("#dasDOI").change(toggleDasDoiRadio);
	$("#ignoreDOI").change(toggleIgnoreDoiRadio);

}


function toggleIgnoreDoiRadio() {
    externalDoiRadio = document.getElementById("ignoreDOI");
    if (externalDoiRadio.checked==true) {
        $("#doiCol").hide();
        $("#doiSource").val('ignore');
    }
}

function toggleDasDoiRadio() {
    externalDoiRadio = document.getElementById("dasDOI");
    if (externalDoiRadio.checked==true) {
        $("#doiCol").hide();
        $("#doiSource").val('das');
    }
}

function toggleExternalDoiRadio() {
    externalDoiRadio = document.getElementById("externalDOI");
    if (externalDoiRadio.checked==true) {
        $("#doiCol").show();
        $("#doiSource").val('external');
    }
}



function stylesAutocomplete() {
    $.ajax({
      type: 'GET',
      url: '/citations/styles/?json',
      success: function(response) {
        var stylesData = {};
        var stylesArray = JSON.parse(response);

        for (var i = 0; i < stylesArray.length; i++) {
            stylesData[stylesArray[i]] = null;
            console.log(stylesArray[i]);
        };
        $("#style").autocomplete(
            {
                minLength: 2,
                limit: 10,
                data: stylesData,
            }
        );
      }
    });
};



function copyCitation() {
  /* Get the text field */
  var copyText = document.getElementById("citation");

  /* Select the text field */
  copyText.select();

  /* Copy the text inside the text field */
  document.execCommand("copy");
}



function updateCitationRow() {
    var dapUrl = null;
    var doi = null;
    var doiSource = null;

    if ($("#dapUrl").length) {
	    var dapUrl = $("#dapUrl").val().trim();
	}
	if ($("#doiSource").length) {
	    var doiSource = $("#doiSource").val().trim()
	    if (doiSource == 'external') {
	        if ($("#doi").length) {
	            var doi = $("#doi").val().trim()
	        }
    	}
	}

	$.ajax({
		url : "/citations/format/",
		data : {
		    doi : doi,
			dapUrl : dapUrl,
			doiSource: doiSource,
			style : $("#style").val()
		},
		dataType : "json",
		success : function(data) {
		    $("#citation").val(data.snippet);
            M.textareaAutoResize($('#citation'));
			$("#citation_row").show();
			if ($("#doiSource").length) {
			    $("#error_row").show();
	            $("#error_row").text(data.error);
			}


		},
		error : function(jqXHR, textStatus, errorThrown) {
			$("#citation_row").hide();
			alert(jqXHR.responseText);
		}


	});
	return false;
}




$(document).ready(init);




