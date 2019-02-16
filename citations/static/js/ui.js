function init() {
    document.getElementById('formatCitation').onsubmit = updateCitationRow;
    //document.getElementById('metadata').onclick = toMetadata;
    stylesAutocomplete();
	$("#doiCol").hide();
	$("#externalDOI").change(toggleExternalDoiRadio);
	$("#dasDOI").change(toggleDasDoiRadio);
	$("#ignoreDOI").change(toggleIgnoreDoiRadio);
    document.getElementById("dasDOI").checked = true;
}

function toMetadata() {
    document.getElementById('formatCitation').action='/citations/metadata'
    document.getElementById('formatCitation').submit();
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
    data = {};

    if ($("#dapUrl").length) {
	    data.dapUrl = $("#dapUrl").val().trim();
	}

	if ($("#doiSource").length) {
	    data.doiSource = $("#doiSource").val().trim();
	}

    if ($("#doi").length) {
        data.doi = $("#doi").val().trim();
    }

    if ($("#style").length) {
        data.style = $("#style").val();
    }

    $("#citation_row").hide();
    $("#error_row").hide();

	$.ajax({
		url : "/citations/make_snippet/",
		dataType : "json",
		data : data,
		success : function(data) {
		    if (data.snippet) {
		        $("#citation").val(data.snippet);
		        $("#request_url").text(data.url);
                M.textareaAutoResize($('#citation'));
			    $("#citation_row").show();
            }
            if (data.error.length>0) {
                $("#error_row").show();
                list = document.getElementById("error_list");
                list.innerHTML = ''
                for (var i = 0; i < data.error.length; i++) {
                    var item = document.createElement('li');
                    item.appendChild(document.createTextNode(data.error[i]));
                    list.appendChild(item);
                }
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




