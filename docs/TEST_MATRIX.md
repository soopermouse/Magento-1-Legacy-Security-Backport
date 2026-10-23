# Acceptance matrix (all unexecuted)

| Runtime | Magento CE 1.9.2.x | Magento CE 1.9.3.x | PHP regression | Apache/mod_php |
|---|---|---|---|---|
| PHP 5.5.38 | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| PHP 5.6.40 | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |

Test both normal requests and abnormal OOM/multipart paths. Verify extension set on the *actual Apache SAPI*, not only CLI. Payment/order tests must use a sandbox and disposable test data. No production claim is authorized from this matrix.
