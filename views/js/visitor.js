$(function () {
    $('#contact').on('submit', function (e) {
        e.preventDefault();  //prevent form from submitting
        let data = {};
        data.otp = $('#otp').val();
        data.phone_number = getUrlParameter("phone");
        let json_data = JSON.stringify(data);
        console.log(json_data);
        user_request(json_data);
    });
});

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
            var user_name = null;
            if (res) {
                message = 'The user was granted access through SmartDoor!';
                console.log("res ====", res)
                // Override username value from API response - username
                user_name = res["user_name"];
                console.log(user_name);
            }
            console.log(res);
            window.location.href = "../html/door.html?user_name=" + user_name;
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

