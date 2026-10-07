FROM composer:2.9 AS composer
FROM php:8.3-cli-bookworm
COPY --from=composer /usr/bin/composer /usr/local/bin/composer
RUN apt-get update && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /tests
COPY php/composer.json php/composer.lock ./
RUN composer install --no-interaction --no-plugins --no-scripts --prefer-dist
COPY php/test.php php/router.php ./
CMD ["php", "test.php"]
