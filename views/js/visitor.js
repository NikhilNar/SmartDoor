// ajax request - POST - User authorization through SmartDoor
function user_request(payload) {
    $.ajax({
        method: 'POST',
        // Add URL from API endpoint
        url: ' https://ccg20ezekb.execute-api.us-west-2.amazonaws.com/Prod/gain_access',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(payload),
        success: function (res) {
            let message = 'Incorrect. Please try again.';
            if (res) {
                message = 'The user was granted access through SmartDoor!';

                 // Override username value from API response - username
				 var response = JSON.parse(res);
				 var user_name = response["body"].user_name;
				 console.log(user_name);
				 var user = getUserInfo(user_name);
				 console.log(user);
            }
            $('#answer').html(message).css("color", "green");
            $('#contact-submit').prop('disabled', true);
            console.log(res);
            console.log(message);
        },
        error: function (err) {
            let message_obj = JSON.parse(err.responseText);
            let message = message_obj.message.content;
            $('#answer').html('Error:' + message).css("color", "red");
            console.log(err);
        }
    });
}

var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
        }
    }
};

// Set username in door.html
var user = function getUserInfo(user_name) {
	console.log(user_name)
	localStorage.setItem("username", user_name);  
}