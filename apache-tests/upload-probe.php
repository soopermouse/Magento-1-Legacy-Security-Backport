<?php
/* TEMPORARY LOCAL-ONLY PROBE. No file is moved or retained. */
header('Content-Type: application/json');
$remote = isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '';
if (!in_array($remote, array('127.0.0.1', '::1'), true)) { http_response_code(403); exit; }
$files = array();
foreach ($_FILES as $key=>$file) { $files[$key] = array('error'=>$file['error'], 'size'=>$file['size'], 'is_uploaded'=>is_uploaded_file($file['tmp_name'])); }
echo json_encode(array('sapi'=>php_sapi_name(),'file_count'=>count($_FILES),'files'=>$files,'post_count'=>count($_POST)));
