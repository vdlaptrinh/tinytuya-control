#!/usr/bin/env python3.11
"""Telegram Bot - Displays temperature & humidity correctly"""

import json
import logging
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import tinytuya

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

CONFIG_PATH = "/Users/dailuu/Desktop/CT2026/tuya2/config.json"
SNAPSHOT_PATH = "/Users/dailuu/Desktop/CT2026/tuya2/snapshot.json"

def load_devices():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        devices = config.get('IOT_DEVICES', {})
        snapshot_dict = {}
        try:
            with open(SNAPSHOT_PATH, 'r', encoding='utf-8') as f:
                snapshot = json.load(f)
            for dev in snapshot.get('devices', []):
                snapshot_dict[dev.get('id')] = dev
        except:
            pass
        filtered = {}
        for name, info in devices.items():
            dev_id = info.get('device_id', '')
            ip = info.get('ip_address', '')
            if not ip:
                snap = snapshot_dict.get(dev_id, {})
                ip = snap.get('ip', '')
            if ip and ip.strip() and ip != 'N/A':
                info['ip'] = ip
                ver = info.get('version')
                if not ver:
                    snap = snapshot_dict.get(dev_id, {})
                    ver = snap.get('ver', 3.3)
                info['version'] = float(ver)
                filtered[name] = info
        return filtered
    except Exception as e:
        print(f"Error: {e}")
        return {}

def get_device_type(name, info):
    product = info.get('product_name', '').lower()
    if 'bulb' in product:
        return 'bulb'
    if 'ir' in product or 'infrared' in product:
        return 'ir'
    if any(x in product for x in ['switch', 'socket', 'cb0', 'aubess', 'tyzx']):
        return 'outlet'
    return 'outlet'

def get_device_instance(name, info):
    dev_type = get_device_type(name, info)
    if dev_type == 'bulb':
        return tinytuya.BulbDevice(
            info['device_id'], info['ip'], info['local_key'], 
            version=info['version'])
    else:
        return tinytuya.OutletDevice(
            info['device_id'], info['ip'], info['local_key'], 
            version=info['version'])

def format_dps_value(name, key, value):
    """Format DPS values for display - Special handling for IR device"""
    # IR Thong Minh - temperature and humidity
    if 'IR_Thong_Minh' in name or 'ir' in name.lower():
        if key == '101':
            # Temperature: raw value / 10 = actual temperature
            temp = value / 10.0
            return f"Nhiet do: {temp}°C"
        elif key == '102':
            return f"Do am: {value}%"
    return f"DPS {key}: {value}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "TinyTuya Telegram Bot\n\n"
    msg += "Commands:\n"
    msg += "/start - Show help\n"
    msg += "/list - List devices\n"
    msg += "/on <device> [switch] - Turn on\n"
    msg += "/off <device> [switch] - Turn off\n"
    msg += "/status <device> - Get status\n"
    msg += "/allon - Turn on all\n"
    msg += "/alloff - Turn off all\n\n"
    msg += "Examples:\n"
    msg += "  /on Den_Gac 2 - Turn on SW2\n"
    msg += "  /status IR_Thong_Minh - Show temp & humidity\n"
    await update.message.reply_text(msg)

async def list_devices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    devices = load_devices()
    if not devices:
        await update.message.reply_text("No devices found!")
        return
    msg = "Devices with IP:\n"
    for name, info in devices.items():
        dtype = get_device_type(name, info)
        msg += f"\n[{dtype}] {name}\n"
        msg += f"  IP: {info['ip']} | Ver: {info['version']}\n"
    await update.message.reply_text(msg)

async def turn_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /on <device_name> [switch_number]")
        return
    
    device_name = context.args[0]
    switch_num = None
    if len(context.args) > 1:
        try:
            switch_num = int(context.args[1])
        except:
            await update.message.reply_text("Switch must be a number (1-4)")
            return
    
    devices = load_devices()
    if device_name not in devices:
        await update.message.reply_text(f"Device '{device_name}' not found!")
        return
    
    info = devices[device_name]
    try:
        dev = get_device_instance(device_name, info)
        if switch_num:
            dev.turn_on(switch=switch_num)
            await update.message.reply_text(f"Turned ON: {device_name} [SW{switch_num}]")
        else:
            dev.turn_on()
            await update.message.reply_text(f"Turned ON: {device_name} [All switches]")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def turn_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /off <device_name> [switch_number]")
        return
    
    device_name = context.args[0]
    switch_num = None
    if len(context.args) > 1:
        try:
            switch_num = int(context.args[1])
        except:
            await update.message.reply_text("Switch must be a number (1-4)")
            return
    
    devices = load_devices()
    if device_name not in devices:
        await update.message.reply_text(f"Device '{device_name}' not found!")
        return
    
    info = devices[device_name]
    try:
        dev = get_device_instance(device_name, info)
        if switch_num:
            dev.turn_off(switch=switch_num)
            await update.message.reply_text(f"Turned OFF: {device_name} [SW{switch_num}]")
        else:
            dev.turn_off()
            await update.message.reply_text(f"Turned OFF: {device_name} [All switches]")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def get_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /status <device_name>")
        return
    device_name = context.args[0]
    devices = load_devices()
    if device_name not in devices:
        await update.message.reply_text(f"Device '{device_name}' not found!")
        return
    info = devices[device_name]
    try:
        dev = get_device_instance(device_name, info)
        data = dev.status()
        dps = data.get('dps', {})
        msg = f"Status: {device_name}\n"
        for key, value in dps.items():
            msg += f"  {format_dps_value(device_name, key, value)}\n"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def all_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    devices = load_devices()
    results = []
    for name, info in devices.items():
        try:
            dev = get_device_instance(name, info)
            dev.turn_on()
            results.append(f"ON: {name}")
        except Exception as e:
            results.append(f"ERR: {name} - {e}")
    await update.message.reply_text("\n".join(results))

async def all_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    devices = load_devices()
    results = []
    for name, info in devices.items():
        try:
            dev = get_device_instance(name, info)
            dev.turn_off()
            results.append(f"OFF: {name}")
        except Exception as e:
            results.append(f"ERR: {name} - {e}")
    await update.message.reply_text("\n".join(results))

def main():
    if len(sys.argv) < 2:
        print("Usage: python3.11 telegram_bot.py <BOT_TOKEN>")
        print("Get token from @BotFather on Telegram")
        return
    TOKEN = sys.argv[1]
    
    logger.info("Starting bot...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_devices))
    app.add_handler(CommandHandler("on", turn_on))
    app.add_handler(CommandHandler("off", turn_off))
    app.add_handler(CommandHandler("status", get_status))
    app.add_handler(CommandHandler("allon", all_on))
    app.add_handler(CommandHandler("alloff", all_off))
    
    logger.info("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
