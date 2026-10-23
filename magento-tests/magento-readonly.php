<?php
/* Run from Magento root using patched PHP CLI. No Magento bootstrap and no writes. */
$root = isset($argv[1]) ? realpath($argv[1]) : getcwd();
$required = array('app/Mage.php', 'app/etc/local.xml', 'index.php', 'cron.php');
$missing = array(); foreach ($required as $path) { if (!is_file($root . DIRECTORY_SEPARATOR . $path)) $missing[]=$path; }
$exts = array('curl','dom','gd','hash','iconv','json','mbstring','mcrypt','openssl','pdo_mysql','simplexml','soap');
$absent=array(); foreach ($exts as $ext) { if (!extension_loaded($ext)) $absent[]=$ext; }
$result=array('php'=>PHP_VERSION,'sapi'=>php_sapi_name(),'magento_root'=>$root,'missing_files'=>$missing,'missing_extensions'=>$absent,'local_xml_present'=>is_file($root.'/app/etc/local.xml'));
echo json_encode($result, JSON_PRETTY_PRINT) . "\n";
exit(count($missing) || count($absent) ? 1 : 0);
