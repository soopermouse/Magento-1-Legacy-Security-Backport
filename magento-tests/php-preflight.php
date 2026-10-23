<?php
/* Run via the target PHP CLI; this does not replace mod_php or functional Magento tests. */
$versions = array('5.5', '5.6');
$extensions = array('PDO', 'pdo_mysql', 'mcrypt', 'gd', 'curl', 'mbstring', 'dom', 'SimpleXML', 'soap', 'iconv', 'openssl', 'zlib', 'session', 'json');
echo 'PHP version: ' . PHP_VERSION . PHP_EOL;
echo 'SAPI: ' . php_sapi_name() . PHP_EOL;
$version = PHP_MAJOR_VERSION . '.' . PHP_MINOR_VERSION;
if (!in_array($version, $versions, true)) { fwrite(STDERR, "Unsupported PHP version for this test matrix\n"); exit(2); }
$missing = array();
foreach ($extensions as $extension) {
    $ok = extension_loaded($extension);
    echo ($ok ? 'OK ' : 'MISSING ') . $extension . PHP_EOL;
    if (!$ok) $missing[] = $extension;
}
if ($missing) { fwrite(STDERR, "Missing modules; verify exact Magento and plugin requirements.\n"); exit(1); }
echo "Basic extension preflight passed. Magento behavior and CVE remediation are NOT verified.\n";
