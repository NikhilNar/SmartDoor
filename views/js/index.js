// Call AWS SDK using apigClient.js
var apigClient = apigClientFactory.newClient();

return new Promise(function (resolve, reject) {

    var params = {};
    
    // Get user input from front-end
    otp = $(".OTP").val();
    console.log("OTP entered by user : ", otp)

    // Visitor's OTP - passcode
	var body = {
		"passcode": otp
    };
    
	var additionalParams = {};

	apigClient.chatbotPost(params, body, additionalParams)
		.then(function (result) {
			console.log("API response - Result: ", result)

            // Reset the OTP field  
            $(".OTP").val(null);
            
			// botMessage = result.data.message.message;
			// console.log("Bot Message: "+ botMessage);
			// resolve(botMessage);

		}).catch(function (result) {
            
		    // Add error callback code here
			console.log("API response - Error : ", result);
			botMessage = "Couldn't establish connection to API Gateway"
			reject(result);
		});
})

