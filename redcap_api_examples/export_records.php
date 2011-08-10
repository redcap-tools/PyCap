<?php
# the class that performs the API call
require_once('RestCallRequest.php');

# arrays to contain elements you want to filter results by
# example: array('item1', 'item2', 'item3');
$records = array();
$events = array();
$fields = array();
$forms = array();

# an array containing all the elements that must be submitted to the API
$data = array('content' => 'record', 'type' => 'flat', 'format' => 'csv', 'records' => $records, 'events' => $events, 
	'fields' => $fields, 'forms' => $forms, 'token' => 'YOUR_TOKEN');

# create a new API request object
$request = new RestCallRequest("API_URL", 'POST', $data);

# initiate the API request
$request->execute();


/********* Handle the return from the API *********/
# OPTION 1: for testing purposes and small datasets you can just output the data to screen

# get the content type of the data being returned
$response = $request->getResponseInfo();
$type = explode(";", $response['content_type']);
$contentType = $type[0];

# set the content type of page
//header("Content-type: $contentType; charset=utf-8");

#print the data to the screen
echo $request->getResponseBody();

# the following line will print out the entire HTTP request object 
# good for testing purposes to see what is sent back by the API and for debugging
//echo '<pre>' . print_r($request, true) . '</pre>';

# OPTION 2: save the output to a file
/*
$filename = 'PATH_AND_FILENAME';
file_put_contents($filename, $request->getResponseBody());
*/




