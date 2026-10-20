<?php
$directory = getenv('RECIPE_FIXTURE_DIR');
file_put_contents($directory . '/requests', json_encode(['path' => $_SERVER['REQUEST_URI'], 'key' => $_SERVER['HTTP_X_API_KEY'] ?? '', 'body' => json_decode(file_get_contents('php://input'), true)]) . "\n", FILE_APPEND);
$status = (int) file_get_contents($directory . '/status');
http_response_code($status);
header('Content-Type: application/json');
header('Retry-After: 60');
echo json_encode($status === 202 ? ['request_id' => 'fixture-request', 'queued_at' => '2026-10-07T00:00:00Z'] : ['message' => 'Fixture rate limit']);
