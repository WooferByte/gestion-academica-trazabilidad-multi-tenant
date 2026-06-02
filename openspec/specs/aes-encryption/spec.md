## ADDED Requirements

### Requirement: Cifrado AES-256-GCM para PII

El sistema SHALL proveer funciones de cifrado y descifrado autenticado usando AES-256 en modo GCM para proteger datos PII (DNI, CUIL, CBU, email) en reposo.

#### Scenario: Cifrado round-trip

- **GIVEN** un texto plano `"12345678"`
- **WHEN** se cifra con `encrypt()`
- **THEN** el resultado es un string base64
- **AND** `decrypt(resultado)` retorna `"12345678"`

#### Scenario: Mismo plaintext produce distinto ciphertext

- **GIVEN** un texto plano `"mismo_valor"`
- **WHEN** se cifra dos veces
- **THEN** los ciphertexts son distintos entre sí (nonce aleatorio)

#### Scenario: Descifrado con nonce corrupto falla

- **GIVEN** un ciphertext válido
- **WHEN** se modifica cualquier byte del nonce
- **THEN** `decrypt()` lanza `EncryptionError`

#### Scenario: Descifrado con clave incorrecta falla

- **GIVEN** un ciphertext cifrado con clave K1
- **WHEN** se descifra con clave K2 (distinta)
- **THEN** `decrypt()` lanza `EncryptionError`

#### Scenario: Encryption key validada en Settings

- **GIVEN** una variable de entorno `ENCRYPTION_KEY`
- **WHEN** la variable tiene longitud distinta de 32 caracteres
- **THEN** el sistema rechaza la configuración al iniciar con error de validación
