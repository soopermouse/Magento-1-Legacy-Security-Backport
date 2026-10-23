# Supported target matrix (planned)

| Magento | PHP 5.5.38 | PHP 5.6.40 |
| --- | --- | --- |
| CE 1.9.2.x | Planned, untested | Planned, untested |
| CE 1.9.3.x | Planned, untested | Planned, untested |

The PHP tarballs are upstream baselines, not distribution RPM sources. RHEL/CentOS 7 packages require separate vendor source RPM selection, dependency mapping and ABI compatibility verification. A generic source patch cannot be advertised as a universal installable RPM.

Validation includes database connectivity, sessions, login, product image upload, XML, SOAP, GD, curl, OpenSSL, mcrypt, checkout (sandbox), cron and third-party extensions. Magento core is not modified.
