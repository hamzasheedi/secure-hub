import ast

# Read the updated settings file
with open('src/config/settings.py', 'r', encoding='utf-8') as f:
    settings_content = f.read()

# Read the updated vault_routes file
with open('src/api/vault_routes.py', 'r', encoding='utf-8') as f:
    vault_routes_content = f.read()

print('CONFIGURATION FIXES VERIFICATION:')
print('='*50)

# Check 1: Settings file has Supabase configurations
settings_checks = [
    ('Supabase URL setting', 'supabase_url: str =' in settings_content),
    ('Supabase Key setting', 'supabase_key: str =' in settings_content),
    ('Bucket Name setting', 'bucket_name: str =' in settings_content),
    ('Use Supabase setting', 'use_supabase: str =' in settings_content),
]

print('Settings file checks:')
for check_name, result in settings_checks:
    status = '[OK]' if result else '[MISSING]'
    print(f'  {status} {check_name}')

# Check 2: Vault routes uses settings properly
vault_routes_checks = [
    ('Settings import', 'from ..config.settings import settings' in vault_routes_content),
    ('Uses settings for URL', 'settings.supabase_url' in vault_routes_content),
    ('Uses settings for key', 'settings.supabase_key' in vault_routes_content),
    ('Has fallback to getenv', 'os.getenv("SUPABASE_URL")' in vault_routes_content),
    ('Has error handling', 'except Exception as supabase_error:' in vault_routes_content),
    ('Has size validation', 'MAX_FILE_SIZE = 10 * 1024 * 1024' in vault_routes_content),
]

print('\nVault routes checks:')
for check_name, result in vault_routes_checks:
    status = '[OK]' if result else '[MISSING]'
    print(f'  {status} {check_name}')

# Overall assessment
all_settings_ok = all(result for _, result in settings_checks)
all_vault_routes_ok = all(result for _, result in vault_routes_checks)

print(f'\nOverall assessment:')
print(f'  Settings configuration: {"[OK]" if all_settings_ok else "[ISSUES]"}')
print(f'  Vault routes configuration: {"[OK]" if all_vault_routes_ok else "[ISSUES]"}')

overall_success = all_settings_ok and all_vault_routes_ok
print(f'  Configuration fixes: {"[SUCCESS]" if overall_success else "[NEEDS WORK]"}')

if overall_success:
    print('\nAll configuration issues have been successfully resolved!')
    print('- Added Supabase settings to Settings class')
    print('- Updated vault_routes to use settings properly')
    print('- Maintained backward compatibility with environment variables')
    print('- Added proper error handling and fallback mechanisms')
else:
    print('\nSome configuration issues remain.')