<?php
/* TEMPORARY LOCAL-ONLY PROBE. Remove immediately after testing. */
header('Content-Type: application/json');
$remote = isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '';
if (!in_array($remote, array('127.0.0.1', '::1'), true)) { http_response_code(403); exit; }
$keys = array('max_multipart_body_parts', 'max_file_uploads', 'post_max_size', 'upload_max_filesize', 'memory_limit', 'session.upload_progress.enabled');
$ini = array(); foreach ($keys as $key) { $v = ini_get($key); $ini[$key] = ($v === false ? null : $v); }
echo json_encode(array('sapi'=>php_sapi_name(),'version'=>PHP_VERSION,'ini'=>$ini,'extensions'=>get_loaded_extensions()));
