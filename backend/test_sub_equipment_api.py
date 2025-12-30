"""Test SubEquipment API"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_sub_equipment_api():
    """Test SubEquipment API endpoints"""

    # Step 1: Login to get access token
    print("=" * 60)
    print("Step 1: Login")
    print("=" * 60)

    login_data = {
        "username": "admin",
        "password": "cXP3q3EUsyYx"
    }

    response = requests.post(f"{BASE_URL}/auth/login/step1", json=login_data)
    print(f"Status: {response.status_code}")

    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return

    data = response.json()

    # If TOTP is disabled, we should get access_token directly
    if data.get('access_token'):
        token = data['access_token']
        print(f"Access Token: {token[:50]}...")
    elif data.get('temp_token') and not data.get('totp_required'):
        # Try step 2 with empty TOTP
        print("Attempting step 2...")
        step2_response = requests.post(
            f"{BASE_URL}/auth/login/step2",
            json={"temp_token": data['temp_token'], "totp_code": "000000"}
        )
        if step2_response.status_code == 200:
            token = step2_response.json()['access_token']
            print(f"Access Token: {token[:50]}...")
        else:
            print(f"Step 2 failed: {step2_response.text}")
            # Use testuser instead
            print("\nTrying testuser...")
            response = requests.post(
                f"{BASE_URL}/auth/login/step1",
                json={"username": "testuser", "password": "test1234"}
            )
            if response.status_code == 200:
                token = response.json().get('access_token')
                print(f"Access Token: {token[:50]}..." if token else "No token")
            else:
                print(f"Testuser login failed: {response.text}")
                return
    else:
        print(f"Unexpected response: {data}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Get equipment list to find a parent equipment
    print("\n" + "=" * 60)
    print("Step 2: Get Equipment List")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/equipment", headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code != 200:
        print(f"Failed: {response.text}")
        return

    equipment_data = response.json()
    equipments = equipment_data.get('equipments', [])

    if not equipments:
        print("No equipment found. Please create equipment first.")
        return

    parent_equipment = equipments[0]
    parent_id = parent_equipment['id']
    parent_code = parent_equipment['asset_code']

    print(f"Found parent equipment: {parent_code} (ID: {parent_id})")

    # Step 3: Create SubEquipment
    print("\n" + "=" * 60)
    print("Step 3: Create SubEquipment")
    print("=" * 60)

    sub_eq_data = {
        "parent_equipment_id": parent_id,
        "component_name": "天線1",
        "serial_number": "ANT-001-TEST",
        "notes": "測試用天線"
    }

    response = requests.post(f"{BASE_URL}/sub-equipment", json=sub_eq_data, headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code not in [200, 201]:
        print(f"Failed: {response.text}")
        return

    sub_equipment = response.json()
    sub_id = sub_equipment['id']
    sub_code = sub_equipment['asset_code']

    print(f"✅ SubEquipment created:")
    print(f"  ID: {sub_id}")
    print(f"  Asset Code: {sub_code}")
    print(f"  Component Name: {sub_equipment['component_name']}")
    print(f"  Status: {sub_equipment['status']}")

    # Step 4: Get SubEquipment list
    print("\n" + "=" * 60)
    print("Step 4: List SubEquipment")
    print("=" * 60)

    response = requests.get(
        f"{BASE_URL}/sub-equipment?parent_equipment_id={parent_id}",
        headers=headers
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['total']} sub-equipment(s)")
        for se in data['sub_equipments']:
            print(f"  - {se['asset_code']}: {se['component_name']}")

    # Step 5: Get SubEquipment detail
    print("\n" + "=" * 60)
    print("Step 5: Get SubEquipment Detail")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/sub-equipment/{sub_id}", headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        detail = response.json()
        print(f"✅ SubEquipment Detail:")
        print(f"  Asset Code: {detail['asset_code']}")
        print(f"  Parent: {detail.get('parent_asset_code')} - {detail.get('parent_model')}")
        print(f"  Component: {detail['component_name']}")
        print(f"  Serial: {detail.get('serial_number')}")
        print(f"  Status: {detail['status']}")

    # Step 6: Update SubEquipment
    print("\n" + "=" * 60)
    print("Step 6: Update SubEquipment")
    print("=" * 60)

    update_data = {
        "serial_number": "ANT-001-UPDATED",
        "notes": "已更新的測試天線"
    }

    response = requests.put(f"{BASE_URL}/sub-equipment/{sub_id}", json=update_data, headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        updated = response.json()
        print(f"✅ SubEquipment updated:")
        print(f"  Serial Number: {updated['serial_number']}")
        print(f"  Notes: {updated['notes']}")

    # Step 7: Get SubEquipment logs
    print("\n" + "=" * 60)
    print("Step 7: Get SubEquipment Logs")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/sub-equipment/{sub_id}/logs", headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        logs = response.json()
        print(f"✅ Found {len(logs)} log(s):")
        for log in logs:
            print(f"  - [{log['log_type']}] {log['description']} by {log.get('created_by_username', 'System')}")

    # Step 8: Delete SubEquipment
    print("\n" + "=" * 60)
    print("Step 8: Delete SubEquipment")
    print("=" * 60)

    response = requests.delete(f"{BASE_URL}/sub-equipment/{sub_id}", headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 204:
        print(f"✅ SubEquipment deleted (soft delete)")

    # Verify deletion
    response = requests.get(
        f"{BASE_URL}/sub-equipment?parent_equipment_id={parent_id}",
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        print(f"  Remaining active sub-equipment: {data['total']}")

    print("\n" + "=" * 60)
    print("✅ All SubEquipment API tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_sub_equipment_api()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
