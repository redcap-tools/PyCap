<?php
error_reporting(-1);

# the class that performs the API call
require_once('RestCallRequest.php');

# an array containing all the elements that must be submitted to the API
$data = array('content' => 'file', 'action' => 'delete', 'record' => '', 
			  'field' => '', 'event' => '', 'token' => 'YOUR_TOKEN');

# create a new API request object
$request = new RestCallRequest("API_URL", 'POST', $data);

# initiate the API request
$request->execute();

# Display the response from the API
echo $request->getResponseBody();
