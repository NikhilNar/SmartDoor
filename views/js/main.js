$(function () {
    loadImage();
    $('#contact').on('submit', function (e) {
        e.preventDefault();  //prevent form from submitting
        let data = {};
        data.v_name = $('#v_name').val();
        data.v_number = $('#v_number').val();
        let image_url = getUrlParameter("image");
        if (image_url !== undefined) {
            data.image_url = image_url;
        }
        let json_data = JSON.stringify(data);
        console.log(json_data);
        send_request(json_data);
    });
});

// ajax request - POST method for owner
function send_request(payload) {
    $.ajax({
        method: 'POST',
        url: 'https://ccg20ezekb.execute-api.us-west-2.amazonaws.com/Prod/grant_access',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(payload),
        success: function (res) {
            let message = 'Incorrect. Please try again.';
            if (res) {
                message = 'The user was added Successfully!';
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

// ajax request - POST - User authorization through SmartDoor
function user_request(payload) {
    $.ajax({
        method: 'POST',
        // Add URL from API endpoint
        url: ' https://fvyrkgvj76.execute-api.us-west-2.amazonaws.com/prod/grant_access',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(payload),
        success: function (res) {
            let message = 'Incorrect. Please try again.';
            if (res) {
                message = 'The user was granted access through SmartDoor!';

                 // Override username value from API response - username
                 var username = JSON.parse(res);
                 document.getElementById("username").innerHTML = username.user_name;
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

function loadImage() {
    document.getElementById("visitor-img").src = getUrlParameter("image");
}
