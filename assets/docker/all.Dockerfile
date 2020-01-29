FROM php:7.2-apache

RUN apt-get update && apt-get install -y build-essential libssl-dev zlib1g-dev libpng-dev libjpeg-dev libfreetype6-dev unzip libicu-dev
RUN docker-php-ext-configure gd --with-freetype-dir=/usr/include/ --with-jpeg-dir=/usr/include/ \
    && docker-php-ext-install gd
RUN docker-php-ext-configure intl && docker-php-ext-install intl
RUN docker-php-ext-install pdo pdo_mysql zip

RUN a2enmod rewrite

EXPOSE 80

COPY --chown=www-data ./shopware /var/www/html/

COPY ./php.ini /usr/local/etc/php/conf.d/shopware.php.ini
