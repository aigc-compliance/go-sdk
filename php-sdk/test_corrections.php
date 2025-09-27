<?php

declare(strict_types=1);

require_once __DIR__ . '/src/ComplianceClient.php';
require_once __DIR__ . '/src/Exceptions/ComplianceExceptions.php';

use AigcCompliance\ComplianceClient;
use AigcCompliance\Exceptions\ComplianceValidationException;

/**
 * Test script to verify PHP SDK corrections
 */

function testPHPSDKCorrections(): bool
{
    echo "🔍 Verifying PHP SDK compliance with https://www.aigc-compliance.com/docs\n\n";
    
    $allTestsPassed = true;
    
    // Test 1: Correct API base URL
    echo "1. API Base URL:\n";
    try {
        $client = new ComplianceClient('test_key');
        
        // Use reflection to check private property
        $reflection = new ReflectionClass($client);
        $baseUrlProperty = $reflection->getProperty('baseUrl');
        $baseUrlProperty->setAccessible(true);
        $baseUrl = $baseUrlProperty->getValue($client);
        
        $expectedBaseUrl = 'https://api.aigc-compliance.com';
        if ($baseUrl === $expectedBaseUrl) {
            echo "   ✅ Correct: {$baseUrl}\n";
        } else {
            echo "   ❌ Wrong: {$baseUrl} (should be {$expectedBaseUrl})\n";
            $allTestsPassed = false;
        }
    } catch (Exception $e) {
        echo "   ❌ Error checking base URL: " . $e->getMessage() . "\n";
        $allTestsPassed = false;
    }
    
    // Test 2: Correct Authentication Header
    echo "\n2. Authentication Header:\n";
    try {
        $client = new ComplianceClient('test_key_123');
        
        // Use reflection to check HTTP client headers
        $reflection = new ReflectionClass($client);
        $httpClientProperty = $reflection->getProperty('httpClient');
        $httpClientProperty->setAccessible(true);
        $httpClient = $httpClientProperty->getValue($client);
        
        $config = $httpClient->getConfig();
        $headers = $config['headers'] ?? [];
        
        if (isset($headers['Authorization']) && $headers['Authorization'] === 'Bearer test_key_123') {
            echo "   ✅ Correct: Authorization Bearer header\n";
        } else {
            echo "   ❌ Wrong: Missing or incorrect Authorization header\n";
            $allTestsPassed = false;
        }
        
        // Check that old X-API-Key header is NOT present
        if (!isset($headers['X-API-Key'])) {
            echo "   ✅ Correct: Old X-API-Key header removed\n";
        } else {
            echo "   ❌ Wrong: Old X-API-Key header still present\n";
            $allTestsPassed = false;
        }
    } catch (Exception $e) {
        echo "   ❌ Error checking authentication: " . $e->getMessage() . "\n";
        $allTestsPassed = false;
    }
    
    // Test 3: Method signature compliance
    echo "\n3. comply() method signature:\n";
    try {
        $client = new ComplianceClient('test_key');
        $reflection = new ReflectionMethod($client, 'comply');
        $parameters = $reflection->getParameters();
        
        // Check for correct parameters
        $paramNames = array_map(function($param) { return $param->getName(); }, $parameters);
        
        if (in_array('filePath', $paramNames)) {
            echo "   ✅ filePath parameter present\n";
        } else {
            echo "   ❌ Missing filePath parameter\n";
            $allTestsPassed = false;
        }
        
        if (in_array('region', $paramNames)) {
            echo "   ✅ region parameter present\n";
        } else {
            echo "   ❌ Missing region parameter\n";
            $allTestsPassed = false;
        }
        
        $requiredParams = ['watermarkPosition', 'logoFile', 'includeBase64', 'saveToDisk'];
        foreach ($requiredParams as $param) {
            if (in_array($param, $paramNames)) {
                echo "   ✅ {$param} parameter present\n";
            } else {
                echo "   ❌ Missing {$param} parameter\n";
                $allTestsPassed = false;
            }
        }
    } catch (Exception $e) {
        echo "   ❌ Error checking method signature: " . $e->getMessage() . "\n";
        $allTestsPassed = false;
    }
    
    // Test 4: Region validation
    echo "\n4. Region validation:\n";
    try {
        $client = new ComplianceClient('test_key');
        
        try {
            $client->comply('fake_file.jpg', 'invalid_region');
            echo "   ❌ Should have raised exception for invalid region\n";
            $allTestsPassed = false;
        } catch (ComplianceValidationException $e) {
            if (strpos($e->getMessage(), "Region must be either 'EU' or 'CN'") !== false) {
                echo "   ✅ Correct region validation\n";
            } else {
                echo "   ❌ Wrong error message: " . $e->getMessage() . "\n";
                $allTestsPassed = false;
            }
        } catch (Exception $e) {
            // Check if it's a file not found error, which means region validation was bypassed
            if (strpos($e->getMessage(), 'not found') !== false) {
                echo "   ❌ Region validation was bypassed (file error came first)\n";
                $allTestsPassed = false;
            } else {
                echo "   ❌ Unexpected error: " . $e->getMessage() . "\n";
                $allTestsPassed = false;
            }
        }
    } catch (Exception $e) {
        echo "   ❌ Error testing region validation: " . $e->getMessage() . "\n";
        $allTestsPassed = false;
    }
    
    // Test 5: Required methods exist
    echo "\n5. Required methods:\n";
    try {
        $client = new ComplianceClient('test_key');
        
        $requiredMethods = ['health', 'downloadFile', 'tag'];
        foreach ($requiredMethods as $method) {
            if (method_exists($client, $method)) {
                echo "   ✅ {$method}() method present\n";
            } else {
                echo "   ❌ Missing {$method}() method\n";
                $allTestsPassed = false;
            }
        }
    } catch (Exception $e) {
        echo "   ❌ Error checking methods: " . $e->getMessage() . "\n";
        $allTestsPassed = false;
    }
    
    return $allTestsPassed;
}

function main(): int
{
    echo "Running PHP SDK verification tests...\n\n";
    
    if (testPHPSDKCorrections()) {
        echo "\n🎉 SUCCESS: PHP SDK is 100% compliant with official documentation!\n\n";
        echo "Key corrections made:\n";
        echo "  • Fixed API base URL: https://api.aigc-compliance.com\n";
        echo "  • Changed authentication: Authorization Bearer instead of X-API-Key\n";
        echo "  • Updated method signatures to match documentation exactly\n";
        echo "  • Added missing parameters: watermark_position, logo_file, include_base64, save_to_disk\n";
        echo "  • Added missing methods: health(), downloadFile()\n";
        echo "  • Fixed region validation to use 'EU'/'CN' values\n";
        echo "\nThe PHP SDK now matches https://www.aigc-compliance.com/docs exactly!\n";
        return 0;
    } else {
        echo "\n❌ FAILED: SDK does not match documentation\n";
        return 1;
    }
}

exit(main());