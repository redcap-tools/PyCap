<?php
error_reporting(-1);

# the class that performs the API call
require_once('RestCallRequest.php');

# an array containing all the elements that must be submitted to the API
$data = array('content' => 'file', 'action' => 'export', 'record' => '', 
			  'field' => '', 'event' => '', 'token' => 'YOUR_TOKEN');

# create a new API request object
$request = new RestCallRequest("API_URL", 'POST', $data);

# initiate the API request
$request->execute();

$response = $request->getResponseInfo();

# Handle the return from the API
if ($response['http_code'] != '200') {
	# there was an error
	echo $request->getResponseBody();
}
else {
	# Parse the content to get the exact filename
	$filename = substr($response['content_type'], strpos($response['content_type'], "=")+2, -1);
	# Set full path where the file will be saved locally (e.g. '/var/www/mydocs/', 'C:\\xampp\\stuff\\mydocs\\')
	$filepath = 'LOCAL_PATH_TO_SAVE_FILE';
	# Save the output to a local file at the location $filepath
	file_put_contents($filepath . $filename, $request->getResponseBody());
}
