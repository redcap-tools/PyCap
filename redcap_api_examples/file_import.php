<?php
error_reporting(-1);

# the class that performs the API call
require_once('RestCallRequest.php');

# full path and filename of the file to upload
$file = 'YOUR_FILE';

# an array containing all the elements that must be submitted to the API
$data = array('content' => 'file', 'action' => 'import', 'record' => '', 
			  'field' => '', 'event' => '', 'token' => 'YOUR_TOKEN', 'file' => "@$file");

# create a new API request object
$request = new RestCallRequest("API_URL", 'POST', $data);

# initiate the API request
$request->execute();

# Display the response from the API
echo $request->getResponseBody();
