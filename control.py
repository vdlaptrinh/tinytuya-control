#!/usr/bin/env python3
"""
TinyTuya Device Control Interface
Giao diện điều khiển thiết bị Tuya qua CLI
"""

import tinytuya
import json
import sys
import time

# Load devices from config.json
def load_devices():
    try:
        with open('/Users/dailuu/Desktop/CT2026/tuya2/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('IOT_DEVICES', {})
    except Exception as e:
        print(f"Lỗi đọc config.json: {e}")
        return {}

# Load snapshot for IP and version
def load_snapshot():
    try:
        with open('/Users/dailuu/Desktop/CT2026/tuya2/snapshot.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        snapshot = {}
        for dev in data.get('devices', []):
            snapshot[dev.get('id')] = dev
        return snapshot
    except:
        return {}

# Clear screen
def clear_screen():
    print('\033c', end='')

# Display main menu
def show_main_menu(devices, snapshot):
    clear_screen()
    print("=" * 60)
    print("    TINYTUYA DEVICE CONTROL")
    print("=" * 60)
    print("\nDanh sách thiết bị:\n")
    
    device_list = list(devices.items())
    for idx, (name, info) in enumerate(device_list, 1):
        dev_id = info.get('device_id', '')
        snap = snapshot.get(dev_id, {})
        ip = snap.get('ip', info.get('ip_address', 'N/A'))
        ver = info.get('version', snap.get('ver', 'N/A'))
        product = info.get('product_name', 'Unknown')
        status = "🟢" if ip != 'N/A' else "🔴"
        print(f"  {idx}. {status} {name}")
        print(f"      IP: {ip} | Ver: {ver} | Type: {product}")
    
    print("\n  0. Thoát")
    print("\n" + "=" * 60)
    return device_list

# Bulb control interface
def control_bulb(name, device_info, snapshot):
    dev_id = device_info.get('device_id')
    snap = snapshot.get(dev_id, {})
    ip = snap.get('ip', device_info.get('ip_address', ''))
    key = device_info.get('local_key', '')
    ver = device_info.get('version', float(snap.get('ver', 3.3)))
    
    if not ip or ip == 'N/A':
        print(f"\n❌ Không tìm thấy IP cho thiết bị {name}!")
        input("\nNhấn Enter để quay lại...")
        return
    
    d = tinytuya.BulbDevice(dev_id, ip, key, version=ver)
    d.set_socketPersistent(True)
    
    while True:
        clear_screen()
        print("=" * 60)
        print(f"   ĐIỀU KHIỂN ĐÈN: {name}")
        print("=" * 60)
        
        # Get current status
        try:
            data = d.status()
            dps = data.get('dps', {})
            power = dps.get('20', False)
            mode = dps.get('21', 'N/A')
            bright = dps.get('22', 'N/A')
            temp = dps.get('23', 'N/A')
            
            print(f"\nTrạng thái: {'🟢 BẬT' if power else '🔴 TẮT'}")
            print(f"Chế độ: {mode}")
            print(f"Độ sáng: {bright}")
            print(f"Nhiệt độ màu: {temp}")
        except Exception as e:
            print(f"\n⚠ Không đọc được trạng thái: {e}")
        
        print("\n--- ĐIỀU KHIỂN ---")
        print("  1. Bật đèn")
        print("  2. Tắt đèn")
        print("  3. Đổi màu (Đỏ)")
        print("  4. Đổi màu (Xanh)")
        print("  5. Đổi màu (Xanh lá)")
        print("  6. Đổi màu (Vàng)")
        print("  7. Đặt độ sáng (0-1000)")
        print("  8. Chế độ Trắng")
        print("  9. Chế độ Màu")
        print(" 10. Chế độ Scene")
        print("  0. Quay lại")
        print("\n" + "=" * 60)
        
        choice = input("\nChọn: ").strip()
        
        try:
            if choice == '1':
                d.turn_on()
                print("✅ Đã bật đèn")
                time.sleep(1)
            elif choice == '2':
                d.turn_off()
                print("✅ Đã tắt đèn")
                time.sleep(1)
            elif choice == '3':
                d.set_colour(255, 0, 0)
                print("✅ Đã đổi màu Đỏ")
                time.sleep(1)
            elif choice == '4':
                d.set_colour(0, 0, 255)
                print("✅ Đã đổi màu Xanh")
                time.sleep(1)
            elif choice == '5':
                d.set_colour(0, 255, 0)
                print("✅ Đã đổi màu Xanh lá")
                time.sleep(1)
            elif choice == '6':
                d.set_colour(255, 200, 0)
                print("✅ Đã đổi màu Vàng")
                time.sleep(1)
            elif choice == '7':
                val = input("Nhập độ sáng (10-1000): ").strip()
                d.set_brightness(int(val))
                print(f"✅ Đã đặt độ sáng: {val}")
                time.sleep(1)
            elif choice == '8':
                d.set_mode('white')
                print("✅ Chế độ Trắng")
                time.sleep(1)
            elif choice == '9':
                d.set_mode('colour')
                print("✅ Chế độ Màu")
                time.sleep(1)
            elif choice == '10':
                d.set_mode('scene')
                print("✅ Chế độ Scene")
                time.sleep(1)
            elif choice == '0':
                break
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            time.sleep(2)

# Outlet control interface
def control_outlet(name, device_info, snapshot):
    dev_id = device_info.get('device_id')
    snap = snapshot.get(dev_id, {})
    ip = snap.get('ip', device_info.get('ip_address', ''))
    key = device_info.get('local_key', '')
    ver = device_info.get('version', float(snap.get('ver', 3.3)))
    
    if not ip or ip == 'N/A':
        print(f"\n❌ Không tìm thấy IP cho thiết bị {name}!")
        input("\nNhấn Enter để quay lại...")
        return
    
    d = tinytuya.OutletDevice(dev_id, ip, key, version=ver)
    d.set_socketPersistent(True)
    
    while True:
        clear_screen()
        print("=" * 60)
        print(f"   ĐIỀU KHIỂN CÔNG TẮC: {name}")
        print("=" * 60)
        
        # Get current status
        try:
            data = d.status()
            dps = data.get('dps', {})
            print("\nTrạng thái công tắc:")
            for sw in ['1', '2', '3', '4']:
                if sw in dps:
                    state = '🟢 BẬT' if dps[sw] else '🔴 TẮT'
                    print(f"  SW{sw}: {state}")
        except Exception as e:
            print(f"\n⚠ Không đọc được trạng thái: {e}")
        
        print("\n--- ĐIỀU KHIỂN ---")
        print("  1. Bật SW1")
        print("  2. Tắt SW1")
        print("  3. Bật SW2")
        print("  4. Tắt SW2")
        print("  5. Bật tất cả")
        print("  6. Tắt tất cả")
        print("  7. Trạng thái (refresh)")
        print("  0. Quay lại")
        print("\n" + "=" * 60)
        
        choice = input("\nChọn: ").strip()
        
        try:
            if choice == '1':
                d.turn_on(switch=1)
                print("✅ Đã bật SW1")
                time.sleep(1)
            elif choice == '2':
                d.turn_off(switch=1)
                print("✅ Đã tắt SW1")
                time.sleep(1)
            elif choice == '3':
                d.turn_on(switch=2)
                print("✅ Đã bật SW2")
                time.sleep(1)
            elif choice == '4':
                d.turn_off(switch=2)
                print("✅ Đã tắt SW2")
                time.sleep(1)
            elif choice == '5':
                d.turn_on(switch=1)
                d.turn_on(switch=2)
                print("✅ Đã bật tất cả")
                time.sleep(1)
            elif choice == '6':
                d.turn_off(switch=1)
                d.turn_off(switch=2)
                print("✅ Đã tắt tất cả")
                time.sleep(1)
            elif choice == '7':
                continue
            elif choice == '0':
                break
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            time.sleep(2)

# Cover control interface
def control_cover(name, device_info, snapshot):
    dev_id = device_info.get('device_id')
    snap = snapshot.get(dev_id, {})
    ip = snap.get('ip', device_info.get('ip_address', ''))
    key = device_info.get('local_key', '')
    ver = device_info.get('version', float(snap.get('ver', 3.3)))
    
    if not ip or ip == 'N/A':
        print(f"\n❌ Không tìm thấy IP cho thiết bị {name}!")
        input("\nNhấn Enter để quay lại...")
        return
    
    d = tinytuya.CoverDevice(dev_id, ip, key, version=ver)
    
    while True:
        clear_screen()
        print("=" * 60)
        print(f"   ĐIỀU KHIỂN RÈM: {name}")
        print("=" * 60)
        
        print("\n--- ĐIỀU KHIỂN ---")
        print("  1. Mở rèm")
        print("  2. Đóng rèm")
        print("  3. Dừng")
        print("  4. Trạng thái")
        print("  0. Quay lại")
        print("\n" + "=" * 60)
        
        choice = input("\nChọn: ").strip()
        
        try:
            if choice == '1':
                d.open_cover()
                print("✅ Đang mở rèm...")
                time.sleep(1)
            elif choice == '2':
                d.close_cover()
                print("✅ Đang đóng rèm...")
                time.sleep(1)
            elif choice == '3':
                d.stop_cover()
                print("✅ Đã dừng")
                time.sleep(1)
            elif choice == '4':
                data = d.status()
                print(f"Trạng thái: {data}")
                input("\nNhấn Enter để tiếp tục...")
            elif choice == '0':
                break
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            time.sleep(2)

# Main function
def main():
    devices = load_devices()
    snapshot = load_snapshot()
    
    if not devices:
        print("Không tìm thấy thiết bị nào trong config.json!")
        return
    
    while True:
        device_list = show_main_menu(devices, snapshot)
        
        try:
            choice = input("\nChọn thiết bị (0 để thoát): ").strip()
            
            if choice == '0':
                print("\nTạm biệt!")
                break
            
            idx = int(choice) - 1
            if 0 <= idx < len(device_list):
                name, info = device_list[idx]
                product = info.get('product_name', '').lower()
                
                # Determine device type
                if 'bulb' in product or 'đèn' in name.lower():
                    control_bulb(name, info, snapshot)
                elif 'switch' in product or 'công tắc' in product or 'đèn gác' in name.lower() or 'đèn bếp' in name.lower():
                    control_outlet(name, info, snapshot)
                elif 'socket' in product or 'quạt' in name.lower() or 'ổ cắm' in name.lower():
                    control_outlet(name, info, snapshot)
                elif 'cover' in product or 'rèm' in product:
                    control_cover(name, info, snapshot)
                else:
                    # Default to outlet
                    print(f"\n⚠ Không xác định được loại thiết bị '{product}', dùng Outlet mặc định")
                    time.sleep(1)
                    control_outlet(name, info, snapshot)
            else:
                print("❌ Lựa chọn không hợp lệ!")
                time.sleep(1)
        except ValueError:
            print("❌ Vui lòng nhập số!")
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nTạm biệt!")
            break

if __name__ == '__main__':
    main()
