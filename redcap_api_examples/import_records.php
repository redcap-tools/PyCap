<?php
# the class that performs the API call
require_once('RestCallRequest.php');

# OPTION 1: place your data here in between <<<DATA and DATA, formatted according to the type and format you've set below
$YOUR_DATA = <<<DATA
study_id,age,sex
"test_001",31,0
"test_002",27,1
DATA;

# or OPTION 2: fill the variable with data from a file
//$YOUR_DATA = file_get_contents(YOUR_FILE)

# an array containing all the elements that must be submitted to the API
$data = array('content' => 'record', 'type' => 'eav', 'format' => 'csv', 'token' => 'YOUR_TOKEN', 
	'data' => $YOUR_DATA);

# create a new API request object
$request = new RestCallRequest("API_URL", 'POST', $data);

# initiate the API request
$request->execute();

# the following line will print out the entire HTTP request object 
# good for testing purposes to see what is sent back by the API and for debugging 
//echo '<pre>' . print_r($request, true) . '</pre>';

# print the output from the API 
echo $request->getResponseBody();
