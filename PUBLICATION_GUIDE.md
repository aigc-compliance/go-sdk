# GUÍA DE PUBLICACIÓN REAL - AIGC Compliance SDKs
# =================================================

## PASO 1: CUENTAS NECESARIAS
# ---------------------------

### Python (PyPI) 🐍
1. Cuenta en PyPI: https://pypi.org/account/register/
2. Verificar email
3. Configurar 2FA (obligatorio)
4. Crear API token: https://pypi.org/manage/account/token/

### Node.js (npm) 📦  
1. Cuenta en npm: https://www.npmjs.com/signup
2. Verificar email
3. Configurar 2FA (recomendado)
4. Crear access token: https://www.npmjs.com/settings/tokens

### PHP (Packagist) 🐘
1. Cuenta en Packagist: https://packagist.org/register/
2. Conectar cuenta GitHub/GitLab
3. No requiere tokens (usa Git)

### Java (Maven Central) ☕
1. Cuenta Sonatype OSSRH: https://central.sonatype.org/register/central-portal/
2. Verificar dominio (o usar GitHub)
3. Generar clave GPG
4. Proceso más complejo - puede tomar días

### Go (Go Modules) 🐹
1. Solo necesita repositorio Git público
2. GitHub/GitLab account
3. Sin registro especial necesario

## PASO 2: CONFIGURACIÓN LOCAL
# ---------------------------

### Instalar herramientas necesarias:
# Python
pip install build twine keyring

# Node.js  
npm install -g npm-cli-login

# PHP
composer global require composer/composer

# Java
# Instalar Maven + GPG

## PASO 3: ORDEN DE PUBLICACIÓN RECOMENDADO
# ----------------------------------------

1. 🐹 Go (más fácil - solo git tag)
2. 📦 Node.js (segundo más fácil)  
3. 🐍 Python (relativamente fácil)
4. 🐘 PHP (necesita repo público)
5. ☕ Java (más complejo - puede tardar)