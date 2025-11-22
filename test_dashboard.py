#!/usr/bin/env python3
"""Test script to verify dashboard generation works."""
import sys
import os

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock Home Assistant objects
class MockHass:
    def __init__(self):
        self.data = {}
        
    def config_path(self, *args):
        return os.path.join('/tmp/cleanme_test', *args)

class MockZone:
    def __init__(self, name):
        self.name = name

# Test the dashboard module
def test_dashboard_generation():
    """Test dashboard generation functions."""
    print("Testing CleanMe dashboard generation...")
    
    # Import the dashboard module
    from custom_components.cleanme import dashboard
    
    # Create mock hass instance
    hass = MockHass()
    hass.data['cleanme'] = {
        'zone1': MockZone('Kitchen'),
        'zone2': MockZone('Living Room'),
        'zone3': MockZone('Bedroom'),
    }
    
    print("\n1. Testing generate_dashboard_config()...")
    config = dashboard.generate_dashboard_config(hass)
    print(f"   ✓ Generated dashboard with {len(config['cards'])} cards")
    print(f"   ✓ Title: {config['title']}")
    print(f"   ✓ Path: {config['path']}")
    print(f"   ✓ Icon: {config['icon']}")
    
    print("\n2. Testing generate_basic_dashboard_config()...")
    basic_config = dashboard.generate_basic_dashboard_config(hass)
    print(f"   ✓ Generated basic dashboard with {len(basic_config['cards'])} cards")
    
    print("\n3. Testing create_simple_cards_list()...")
    cards = dashboard.create_simple_cards_list(hass)
    print(f"   ✓ Generated {len(cards)} zone cards")
    
    print("\n4. Testing get_required_custom_cards()...")
    required = dashboard.get_required_custom_cards()
    print(f"   ✓ Required custom cards: {', '.join(required)}")
    
    print("\n5. Verifying card structure...")
    for i, card in enumerate(config['cards'][:-1]):  # Exclude the Add Zone card
        print(f"   Card {i+1}: {card.get('primary', 'N/A')}")
        assert 'type' in card, "Card missing 'type' field"
        assert 'primary' in card, "Card missing 'primary' field"
        assert card['type'] == 'custom:mushroom-template-card', "Wrong card type"
    print(f"   ✓ All cards have required fields")
    
    print("\n6. Verifying basic card structure...")
    for i, card in enumerate(basic_config['cards']):
        print(f"   Basic Card {i+1}: {card.get('title', 'N/A')}")
        assert 'type' in card, "Card missing 'type' field"
        assert 'entities' in card, "Card missing 'entities' field"
        assert card['type'] == 'entities', "Wrong card type"
    print(f"   ✓ All basic cards have required fields")
    
    print("\n✅ All dashboard generation tests passed!")
    return True

if __name__ == '__main__':
    try:
        test_dashboard_generation()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
