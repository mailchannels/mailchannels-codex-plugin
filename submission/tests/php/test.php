<?php
require __DIR__ . '/vendor/autoload.php';
preg_match_all('/^```php\n(.*?)^```/ms', file_get_contents('/recipe.md'), $matches);
$blocks = $matches[1];
function check(bool $ok, string $label): void {
    if (!$ok) { throw new RuntimeException($label); }
}
check(count($blocks) === 3, 'Review recipe structure change');
$directory = sys_get_temp_dir() . '/plugin-recipe-' . bin2hex(random_bytes(8));
mkdir($directory, 0700);
file_put_contents($directory . '/status', '202');
$socket = stream_socket_server('tcp://127.0.0.1:0');
$address = stream_socket_get_name($socket, false);
fclose($socket);
putenv('RECIPE_FIXTURE_DIR=' . $directory);
putenv('MAILCHANNELS_API_URL=http://' . $address . '/tx/v1');
putenv('MAILCHANNELS_API_KEY=fixture-only-key');
$server = proc_open([PHP_BINARY, '-S', $address, __DIR__ . '/router.php'], [0 => ['pipe', 'r'], 1 => ['file', $directory . '/server.log', 'a'], 2 => ['file', $directory . '/server.log', 'a']], $pipes);
try {
    for ($i = 0; $i < 100; $i++) {
        $probe = @stream_socket_client('tcp://' . $address, $errno, $error, .1);
        if ($probe) { fclose($probe); break; }
        usleep(20000);
    }
    check((bool) $probe, 'Fixture HTTP server ready');
    foreach ([202, 429] as $status) {
        file_put_contents($directory . '/status', (string) $status);
        foreach ([1, 2] as $index) {
            file_put_contents($directory . '/requests', '');
            $caught = null;
            try {
                // Preserve setup and operation fences byte-for-byte in one scope.
                (static function ($snippet) { eval($snippet); })($blocks[0] . "\n" . $blocks[$index]);
            } catch (Throwable $error) { $caught = $error; }
            check($status === 202 ? $caught === null : $caught instanceof MailChannels\Exception\RateLimitException, 'Expected outcome: ' . ($caught ? get_class($caught) . ': ' . $caught->getMessage() : 'accepted'));
            $calls = array_values(array_filter(explode("\n", file_get_contents($directory . '/requests'))));
            check(count($calls) === 1, 'Exactly one HTTP request');
            $call = json_decode($calls[0], true);
            check($call['path'] === '/tx/v1/send-async', 'Queue endpoint, no dry-run flag');
            check($call['key'] === 'fixture-only-key', 'Fixture authentication');
            check($call['body']['from']['email'] === ($index === 1 ? 'notifications@example.com' : 'sender@example.com'), 'Sender preserved');
            check($call['body']['personalizations'][0]['to'][0]['email'] === 'recipient@example.net', 'Recipient preserved');
            check($call['body']['content'][0]['type'] === 'text/plain', 'Text content preserved');
        }
    }
    file_put_contents($directory . '/requests', '');
    putenv('MAILCHANNELS_API_KEY');
    $caught = null;
    try { eval($blocks[0]); } catch (RuntimeException $error) { $caught = $error; }
    check($caught?->getMessage() === 'MAILCHANNELS_API_KEY is required', 'Missing-key guard');
    check(file_get_contents($directory . '/requests') === '', 'Missing key makes no request');
    echo json_encode(['sdk' => Composer\InstalledVersions::getPrettyVersion('mailchannels/mailchannels-php'), 'php' => PHP_VERSION, 'fences' => 3, 'runtime_cases' => 5, 'loopback_requests' => 4, 'live_requests' => 0]) . "\n";
} finally {
    proc_terminate($server);
    fclose($pipes[0]);
    proc_close($server);
    foreach (glob($directory . '/*') as $file) { unlink($file); }
    rmdir($directory);
}
